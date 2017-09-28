package tools

import (
	"fmt"
	"io/ioutil"
	"net/http"
	"net/url"
	"time"
	"strings"
)

func createToken(applicationID string, secret string, org string) (string, error) {
	query := url.Values{}
	query.Set("client_id", applicationID)
	query.Set("client_secret", secret)
	query.Set("grant_type", "client_credentials")
	query.Set("response_type", "id_token")
	query.Set("scope", fmt.Sprintf("user:memberof:%s,offline_access", org))
	query.Set("validity", "3500")
	url := fmt.Sprintf("https://itsyou.online/v1/oauth/access_token?%s", query.Encode())
	return requestToken(url, "")
}

func refreshToken(token string) (string, error) {
	query := url.Values{}
	query.Set("validity", "3500")
	url := fmt.Sprintf("https://itsyou.online/v1/oauth/jwt/refresh?%s", query.Encode())
	return requestToken(url, token)
}

func requestToken(url string, jwt string) (string, error) {
	req, err := http.NewRequest("POST", url, nil)
	if err != nil {
		return "", err
	}
	if jwt != "" {
		jwt = strings.Replace(jwt, "Bearer ", "bearer ", 1)
		req.Header.Set("Authorization", jwt)
	}
	client := http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return "", err
	}

	defer resp.Body.Close()

	bodyBytes, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return "", err
	}
	bodyString := string(bodyBytes)

	if resp.StatusCode == 200 { // OK
		bodyString = fmt.Sprintf("Bearer %v", bodyString)
		return bodyString, nil
	}
	err = fmt.Errorf("failed to get jwt from itsyou.online.\nstatus: %d\nerror: %s", resp.StatusCode, bodyString)
	return "", err
}

func GetToken(token string, applicationID string, secret string, org string) (string, error) {
	if token == "" {
		token, err := createToken(applicationID, secret, org)
		if err != nil {
			return "", err
		}
		return token, nil
	}

	claim, err := GetJWTClaim(token)
	if err != nil {
		return "", err
	}
	exp := int64(claim["exp"].(float64))
	now := time.Now().Unix()
	if rem := exp - now; rem < 300{
		token, err = refreshToken(token)
		if err != nil {
			return "", err
		}
	}
	return token, nil
}
