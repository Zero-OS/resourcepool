package main

import (
	"encoding/json"
	"net/http"
)

// ListBridges is the handler for GET /node/{nodeid}/bridge
// List bridges
func (api NodeAPI) ListBridges(w http.ResponseWriter, r *http.Request) {
	var respBody []Bridge
	json.NewEncoder(w).Encode(&respBody)
}
