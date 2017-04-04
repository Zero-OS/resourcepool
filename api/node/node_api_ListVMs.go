package node

import (
	"encoding/json"
	"net/http"
)

// ListVMs is the handler for GET /node/{nodeid}/vm
// List VMs
func (api NodeAPI) ListVMs(w http.ResponseWriter, r *http.Request) {
	var respBody []VMListItem
	json.NewEncoder(w).Encode(&respBody)
}
