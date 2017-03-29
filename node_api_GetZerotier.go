package main

import (
	"encoding/json"
	"net/http"
)

// GetZerotier is the handler for GET /node/{nodeid}/zerotier/{zerotierid}
// Get Zerotier network details
func (api NodeAPI) GetZerotier(w http.ResponseWriter, r *http.Request) {
	var respBody Zerotier
	json.NewEncoder(w).Encode(&respBody)
}
