package main

import (
	"net/http"

	"fmt"
	"github.com/g8os/go-client"
)

// FileDownload is the handler for GET /node/{nodeid}/container/{containerid}/filesystem
// Download file from container
func (api NodeAPI) FileDownload(w http.ResponseWriter, r *http.Request) {
	path := r.URL.Query().Get("path")
	if path == "" {
		WriteError(w, http.StatusBadRequest, fmt.Errorf("missing path"))
		return
	}

	container, err := GetContainerConnection(r)
	if err != nil {
		WriteError(w, http.StatusInternalServerError, err)
	}

	fs := client.Filesystem(container)

	w.Header().Set("content-type", "application/octet-stream")
	if err := fs.Download(path, w); err != nil {
		WriteError(w, http.StatusInternalServerError, err)
	}
}
