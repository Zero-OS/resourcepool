package node

import (
	"net/http"

	"github.com/zero-os/0-orchestrator/api/handlers"
)

// StopVM is the handler for POST /node/{nodeid}/vm/{vmid}/stop
// Stops the VM
func (api *NodeAPI) StopVM(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)
	if err := api.client.ExecuteVMAction(r, "stop"); err != nil {
		handlers.HandleError(w, err)
	}

	w.WriteHeader(http.StatusNoContent)
}
