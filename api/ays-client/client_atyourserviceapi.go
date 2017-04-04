package client

import (
	"net/http"
)

const (
	defaultBaseURI = "https://localhost:5000"
)

type AtYourServiceAPI struct {
	client     http.Client
	AuthHeader string // Authorization header, will be sent on each request if not empty
	BaseURI    string
	common     service // Reuse a single struct instead of allocating one for each service on the heap.

	Ays      *AysService
	Webhooks *WebhooksService
}

type service struct {
	client *AtYourServiceAPI
}

func NewAtYourServiceAPI() *AtYourServiceAPI {
	c := &AtYourServiceAPI{
		BaseURI: defaultBaseURI,
		client:  http.Client{},
	}
	c.common.client = c

	c.Ays = (*AysService)(&c.common)
	c.Webhooks = (*WebhooksService)(&c.common)

	return c
}
