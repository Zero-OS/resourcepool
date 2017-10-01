package node

import (
	"net/http"

	"github.com/zero-os/0-orchestrator/api/tools"
)

// StopVM is the handler for POST /node/{nodeid}/vm/{vmid}/stop
// Stops the VM
func (api *NodeAPI) StopVM(w http.ResponseWriter, r *http.Request) {
	aysClient, err := tools.GetAysConnection(api)
	if err != nil {
		tools.WriteError(w, http.StatusUnauthorized, err, "")
		return
	}
	tools.ExecuteVMAction(aysClient, w, r, api.AysRepo, "stop")
}
