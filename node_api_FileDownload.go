package main

import (
	"net/http"
)

// FileDownload is the handler for GET /node/{nodeid}/container/{containerid}/filesystem
// Download file from container
func (api NodeAPI) FileDownload(w http.ResponseWriter, r *http.Request) {
}
