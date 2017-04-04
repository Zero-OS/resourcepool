package node

import (
	"encoding/json"
	"net/http"
)

// GetBridge is the handler for GET /node/{nodeid}/bridge/{bridgeid}
// Get bridge details
func (api NodeAPI) GetBridge(w http.ResponseWriter, r *http.Request) {
	var respBody Bridge
	json.NewEncoder(w).Encode(&respBody)
}
