package node

import (
	"encoding/json"
	"net/http"
)

// ListNodes is the handler for GET /node
// List Nodes
func (api NodeAPI) ListNodes(w http.ResponseWriter, r *http.Request) {
	var respBody []Node
	json.NewEncoder(w).Encode(&respBody)
}
