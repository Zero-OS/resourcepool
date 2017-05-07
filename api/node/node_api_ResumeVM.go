package node

import (
	"net/http"

	"github.com/g8os/resourcepool/api/tools"
)

// ResumeVM is the handler for POST /nodes/{nodeid}/vms/{vmid}/resume
// Resumes the VM
func (api NodeAPI) ResumeVM(w http.ResponseWriter, r *http.Request) {
	tools.ExecuteVMAction(w, r, api.AysRepo, "resume")
}
