package main

import (
	"fmt"
	"net/http"

	client "github.com/g8os/go-client"
)

// FileUpload is the handler for POST /node/{nodeid}/container/{containerid}/filesystem
// Upload file to container
func (api NodeAPI) FileUpload(w http.ResponseWriter, r *http.Request) {
	path := r.URL.Query().Get("path")
	if path == "" {
		WriteError(w, http.StatusBadRequest, fmt.Errorf("missing path"))
		return
	}

	if err := r.ParseMultipartForm(4 * 1024 * 1024); err != nil { //4MiB
		WriteError(w, http.StatusBadRequest, err)
		return
	}

	defer r.MultipartForm.RemoveAll()

	filesList, ok := r.MultipartForm.File["file"]
	if !ok {
		WriteError(w, http.StatusBadRequest, fmt.Errorf("missing file"))
		return
	}

	file := filesList[0]
	fd, err := file.Open()
	if err != nil {
		WriteError(w, http.StatusInternalServerError, err)
		return
	}

	container, err := GetContainerConnection(r)
	if err != nil {
		WriteError(w, http.StatusInternalServerError, err)
	}

	fs := client.Filesystem(container)

	if err := fs.Upload(fd, path); err != nil {
		WriteError(w, http.StatusInternalServerError, err)
		return
	}
}
