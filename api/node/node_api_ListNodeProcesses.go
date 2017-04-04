package node

import (
	"encoding/json"
	"net/http"
)

// ListNodeProcesses is the handler for GET /node/{nodeid}/process
// Get Processes
func (api NodeAPI) ListNodeProcesses(w http.ResponseWriter, r *http.Request) {
	var respBody []Process
	json.NewEncoder(w).Encode(&respBody)

}
