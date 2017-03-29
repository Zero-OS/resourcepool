package main

import (
	"encoding/json"
	"net/http"
)

// PingContainer is the handler for POST /node/{nodeid}/container/{containerid}/ping
// Ping this container
func (api NodeAPI) PingContainer(w http.ResponseWriter, r *http.Request) {
	var respBody bool
	json.NewEncoder(w).Encode(&respBody)
}
