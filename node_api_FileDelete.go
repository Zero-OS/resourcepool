package main

import (
	"encoding/json"
	"net/http"

	client "github.com/g8os/go-client"
)

// FileDelete is the handler for DELETE /node/{nodeid}/container/{containerid}/filesystem
// Delete file from container
func (api NodeAPI) FileDelete(w http.ResponseWriter, r *http.Request) {
	var reqBody DeleteFile

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		w.WriteHeader(400)
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		w.WriteHeader(400)
		w.Write([]byte(`{"error":"` + err.Error() + `"}`))
		return
	}

	container, err := GetContainerConnection(r)
	if err != nil {
		WriteError(w, http.StatusInternalServerError, err)
	}

	fs := client.Filesystem(container)
	if err := fs.Remove(reqBody.Path); err != nil {
		WriteError(w, http.StatusInternalServerError, err)
	}

	w.WriteHeader(http.StatusNoContent)
}
