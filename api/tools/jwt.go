package tools

import (
	"fmt"
	"io/ioutil"
	"net/http"
)

func refreshToken(applicationID string, secret string, org string) (string, error) {
	url := fmt.Sprintf("https://itsyou.online/v1/oauth/access_token?client_id=%s&client_secret=%s&grant_type=client_credentials&response_type=id_token&scope=user:memberof:%s,offline_access", applicationID, secret, org)
	resp, err := http.Post(url, "", nil)
	if err != nil {
		return "", err
	}

	defer resp.Body.Close()

	if resp.StatusCode == 200 { // OK
		bodyBytes, err := ioutil.ReadAll(resp.Body)
		if err != nil {
			return "", err

		}
		bodyString := string(bodyBytes)
		bodyString = fmt.Sprintf("Bearer %v", bodyString)
		return bodyString, nil
	}

	err = fmt.Errorf("invalid appliaction-id and secret")
	return "", err
}

func GetToken(token string, applicationID string, secret string, org string) (string, error) {
	if token == "" {
		token, err := refreshToken(applicationID, secret, org)
		if err != nil {
			return "", err
		}
		return token, nil
	}

	claim, err := GetJWTClaim(token)
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
