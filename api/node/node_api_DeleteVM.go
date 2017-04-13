package node

import (
	"net/http"

	"github.com/gorilla/mux"

	log "github.com/Sirupsen/logrus"
	tools "github.com/g8os/grid/api/tools"
)

// DeleteVM is the handler for DELETE /nodes/{nodeid}/vms/{vmid}
// Deletes the VM
func (api NodeAPI) DeleteVM(w http.ResponseWriter, r *http.Request) {

	vars := mux.Vars(r)
	vmid := vars["vmid"]

	obj := make(map[string]interface{})
	obj["actions"] = []map[string]string{map[string]string{"action": "stop", "actor": "vm", "service": vmid}}

	run, err := tools.ExecuteBlueprint(api.AysRepo, "vm", vmid, "delete", obj)
	if err != nil {
		log.Errorf("Error executing blueprint for vm %s deletion : %+v", vmid, err)
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	if err := tools.WaitRunDone(run.Key, api.AysRepo); err != nil {
		log.Errorf("Error while waiting for vm %s deletion : %+v", vmid, err)
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	if err := tools.DeleteServiceByName(vmid, "vm", api.AysRepo); err != nil {
		log.Errorf("Error while deleting vm service %s : %+v", vmid, err)
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}
}
