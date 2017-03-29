package main

import (
	"encoding/json"
	"net/http"
)

// ListZerotier is the handler for GET /node/{nodeid}/zerotier
// List running Zerotier networks
func (api NodeAPI) ListZerotier(w http.ResponseWriter, r *http.Request) {
	var respBody []ZerotierListItem
	json.NewEncoder(w).Encode(&respBody)
}
