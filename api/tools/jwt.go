package tools

import (
	"fmt"
	"io/ioutil"
	"net/http"
	"net/url"
	"sync"
	"time"
)

type JWTProvider struct {
	jwt         string
	updateLock  *sync.Mutex
	expires     int64
	development bool
}

func NewJWTProvider(jwt string) (*JWTProvider, error) {
	jp := new(JWTProvider)
	jp.jwt = jwt
	jp.expires = 0
	jp.updateLock = new(sync.Mutex)

	if err := jp.doRefreshToken(); err != nil {
		return nil, err
	}
	return jp, nil
}

func NewDevelopmentJWTProvider() *JWTProvider {
	var jp JWTProvider
	jp.development = true
	return &jp
}

func (jp *JWTProvider) doRefreshToken() error {
	query := url.Values{}
	query.Set("validity", "3500")
	url := fmt.Sprintf("https://itsyou.online/v1/oauth/jwt/refresh?%s", query.Encode())
	req, err := http.NewRequest("POST", url, nil)
	if err != nil {
		return err
	}
	authString := fmt.Sprintf("bearer %v", jp.jwt)
	req.Header.Set("Authorization", authString)
	client := http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return err
	}

	defer resp.Body.Close()

	bodyBytes, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return err
	}
	bodyString := string(bodyBytes)

	if resp.StatusCode == 200 { // OK
		jp.jwt = bodyString
		claim, err := GetJWTClaim(jp.jwt)
		if err != nil {
			return err
		}
		jp.expires = int64(claim["exp"].(float64))
		return nil
	}
	err = fmt.Errorf("failed to get jwt from itsyou.online.\nstatus: %d\nerror: %s", resp.StatusCode, bodyString)
	return err
}

func (jp *JWTProvider) refreshToken() (string, error) {
	jwtBeforeLock := jp.jwt
	jp.updateLock.Lock()
	defer jp.updateLock.Unlock()
	if jwtBeforeLock != jp.jwt {
		return jp.jwt, nil
	}

	err := jp.doRefreshToken()
	if err != nil {
		return "", err
	}
	return jp.jwt, nil
}

func (jp *JWTProvider) GetJWT() (string, error) {
	if jp.development {
		return jp.jwt, nil
	}

	now := time.Now().Unix()
	if rem := jp.expires - now; rem < 300 {
		return jp.refreshToken()
	}
	return jp.jwt, nil
}
