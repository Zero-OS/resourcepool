package client

import (
	"net/http"
)

type WebhooksService service

// Endpoint that receives generic events
func (s *WebhooksService) WebhooksEventsPost(body WebhooksEventsPostReqBody, headers, queryParams map[string]interface{}) (*http.Response, error) {

	resp, err := s.client.doReqWithBody("POST", s.client.BaseURI+"/webhooks/events", &body, headers, queryParams)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	return resp, nil
}

// Endpoint that receives the events from github
func (s *WebhooksService) WebhooksGithubPost(headers, queryParams map[string]interface{}) (*http.Response, error) {

	resp, err := s.client.doReqWithBody("POST", s.client.BaseURI+"/webhooks/github", nil, headers, queryParams)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	return resp, nil
}
