package node

import (
	"net/http"
)

// PauseVM is the handler for POST /node/{nodeid}/vm/{vmid}/pause
// Pauses the VM
func (api NodeAPI) PauseVM(w http.ResponseWriter, r *http.Request) {
}
