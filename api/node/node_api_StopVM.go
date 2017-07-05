package node

import (
	"net/http"

	"github.com/zero-os/0-orchestrator/api/tools"
)

// StopVM is the handler for POST /node/{nodeid}/vm/{vmid}/stop
// Stops the VM
func (api NodeAPI) StopVM(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)
	tools.ExecuteVMAction(aysClient, w, r, api.AysRepo, "stop")
}
