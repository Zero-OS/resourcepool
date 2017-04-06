package node

import (
	"encoding/json"
	"net/http"
)

// ListContainerProcesses is the handler for GET /nodes/{nodeid}/containers/{containerid}/process
// Get running processes in this container
func (api NodeAPI) ListContainerProcesses(w http.ResponseWriter, r *http.Request) {
	var respBody []Process
	json.NewEncoder(w).Encode(&respBody)
}
