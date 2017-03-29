package main

import (
	"encoding/json"
	"net/http"
)

// GetContainer is the handler for GET /node/{nodeid}/container/{containerid}
// Get Container
func (api NodeAPI) GetContainer(w http.ResponseWriter, r *http.Request) {
	var respBody Container
	json.NewEncoder(w).Encode(&respBody)
}
