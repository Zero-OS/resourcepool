package main

import (
	"encoding/json"
	"net/http"

	client "github.com/g8os/go-client"
)

// PingContainer is the handler for POST /node/{nodeid}/container/{containerid}/ping
// Ping this container
func (api NodeAPI) PingContainer(w http.ResponseWriter, r *http.Request) {
	var respBody bool
	container, err := GetContainerConnection(r)
	if err != nil {
		WriteError(w, http.StatusInternalServerError, err)
		return
	}

	core := client.Core(container)

	if err := core.Ping(); err != nil {
		respBody = false
	} else {
		respBody = true
	}

	json.NewEncoder(w).Encode(&respBody)
}
