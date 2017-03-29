package main

import (
	"net/http"
)

// FileUpload is the handler for POST /node/{nodeid}/container/{containerid}/filesystem
// Upload file to container
func (api NodeAPI) FileUpload(w http.ResponseWriter, r *http.Request) {
}
