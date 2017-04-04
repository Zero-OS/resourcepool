package node

import (
	"encoding/json"
	"net/http"
)

// GetVMInfo is the handler for GET /node/{nodeid}/vm/{vmid}/info
// Get statistical information about the virtual machine.
func (api NodeAPI) GetVMInfo(w http.ResponseWriter, r *http.Request) {
	var respBody VMInfo
	json.NewEncoder(w).Encode(&respBody)
}
