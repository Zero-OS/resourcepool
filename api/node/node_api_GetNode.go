package node

import (
	"encoding/json"
	"net/http"
)

// GetNode is the handler for GET /node/{nodeid}
// Get detailed information of a node
func (api NodeAPI) GetNode(w http.ResponseWriter, r *http.Request) {
	var respBody Node
	json.NewEncoder(w).Encode(&respBody)
}
