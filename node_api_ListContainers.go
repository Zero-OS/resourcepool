package main

import (
	"encoding/json"
	"net/http"
)

// ListContainers is the handler for GET /node/{nodeid}/container
// List running Containers
func (api NodeAPI) ListContainers(w http.ResponseWriter, r *http.Request) {
	var respBody []ContainerListItem
	json.NewEncoder(w).Encode(&respBody)
}
