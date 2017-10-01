package node

import (
	"net/http"

	"github.com/zero-os/0-orchestrator/api/tools"
)

// ResumeVM is the handler for POST /nodes/{nodeid}/vms/{vmid}/resume
// Resumes the VM
func (api *NodeAPI) ResumeVM(w http.ResponseWriter, r *http.Request) {
	aysClient, err := tools.GetAysConnection(r, api)
	if err != nil {
		tools.WriteError(w, http.StatusUnauthorized, err, "")
		return
	}
	tools.ExecuteVMAction(aysClient, w, r, api.AysRepo, "resume")
}
