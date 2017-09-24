package ays

import (
	"crypto/ecdsa"
	"fmt"
	"io/ioutil"
	"net/http"
	"strings"

	log "github.com/Sirupsen/logrus"
	jwt "github.com/dgrijalva/jwt-go"
)

// JWTPublicKey of itsyou.online
var JWTPublicKey *ecdsa.PublicKey

const (
	oauth2ServerPublicKey = `\
-----BEGIN PUBLIC KEY-----
MHYwEAYHKoZIzj0CAQYFK4EEACIDYgAES5X8XrfKdx9gYayFITc89wad4usrk0n2
7MjiGYvqalizeSWTHEpnd7oea9IQ8T5oJjMVH5cc0H5tFSKilFFeh//wngxIyny6
6+Vq5t5B0V0Ehy01+2ceEon2Y0XDkIKv
-----END PUBLIC KEY-----`

	maxJWTDuration int64 = 3600 //1 hour
)

func init() {
	var err error

	if len(oauth2ServerPublicKey) == 0 {
		return
	}

	JWTPublicKey, err = jwt.ParseECPublicKeyFromPEM([]byte(oauth2ServerPublicKey))
	if err != nil {
		log.Fatalf("failed to parse pub key:%v", err)
	}
}

func getToken(token string, applicationID string, secret string, org string) (string, error) {
	log.Debug("generate token")

	if token == "" {
		token, err := refreshToken(applicationID, secret, org)
		if err != nil {
			return "", err
		}
		return token, nil
	}

	claim, err := getJWTClaim(token)
	if err != nil {
		return "", err
	}
	exp := claim["exp"].(float64)
	if exp < 300 {
		token, err = refreshToken(applicationID, secret, org)
		if err != nil {
			return "", err
		}
	}
	return token, nil
}

func refreshToken(applicationID string, secret string, org string) (string, error) {
	log.Debug("refresh token")
	url := fmt.Sprintf("https://itsyou.online/v1/oauth/access_token?client_id=%s&client_secret=%s&grant_type=client_credentials&response_type=id_token&scope=user:memberof:%s,offline_access&validity=3600", applicationID, secret, org)
	resp, err := http.Post(url, "", nil)
	if err != nil {
		return "", err
	}

	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("invalid appliaction-id and secret")
	}

	bodyBytes, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return "", err
	}

	token := string(bodyBytes)
	return token, nil
}

func getJWTClaim(tokenStr string) (jwt.MapClaims, error) {
	jwtStr := strings.TrimSpace(strings.TrimPrefix(tokenStr, "Bearer"))
	token, err := jwt.Parse(jwtStr, func(token *jwt.Token) (interface{}, error) {
		if token.Method != jwt.SigningMethodES384 {
			return nil, fmt.Errorf("Unexpected signing method: %v", token.Header["alg"])
		}
		return JWTPublicKey, nil
	})

	if err != nil {
		return nil, err
	}

	claims, ok := token.Claims.(jwt.MapClaims)
	if !ok {
		return nil, fmt.Errorf("Invalid claims")
	}

	return claims, nil
}
