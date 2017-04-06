package node

import (
	"encoding/json"
	"net/http"
)

// GetNodeProcess is the handler for GET /node/{nodeid}/process/{proccessid}
// Get process details
func (api NodeAPI) GetNodeProcess(w http.ResponseWriter, r *http.Request) {
	var respBody Process
	json.NewEncoder(w).Encode(&respBody)
}
