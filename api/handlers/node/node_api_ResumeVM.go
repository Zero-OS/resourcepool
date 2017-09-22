package node

import (
	"net/http"

	"github.com/zero-os/0-orchestrator/api/handlers"
)

// ResumeVM is the handler for POST /nodes/{nodeid}/vms/{vmid}/resume
// Resumes the VM
func (api *NodeAPI) ResumeVM(w http.ResponseWriter, r *http.Request) {
	if err := api.client.ExecuteVMAction(r, "resume"); err != nil {
		handlers.HandlerError(w, err)
	}
	w.WriteHeader(http.StatusNoContent)
}
