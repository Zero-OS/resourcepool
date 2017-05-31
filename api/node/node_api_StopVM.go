package node

import (
	"net/http"

	"github.com/zero-os/0-orchestrator/api/tools"
)

// StopVM is the handler for POST /node/{nodeid}/vm/{vmid}/stop
// Stops the VM
func (api NodeAPI) StopVM(w http.ResponseWriter, r *http.Request) {
	tools.ExecuteVMAction(w, r, api.AysRepo, "stop")
}
