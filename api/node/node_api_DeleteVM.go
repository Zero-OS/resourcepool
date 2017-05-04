package node

import (
	"net/http"

	"github.com/gorilla/mux"

	log "github.com/Sirupsen/logrus"
	tools "github.com/g8os/grid/api/tools"
	//"fmt"
)

// DeleteVM is the handler for DELETE /nodes/{nodeid}/vms/{vmid}
// Deletes the VM
func (api NodeAPI) DeleteVM(w http.ResponseWriter, r *http.Request) {

	vars := mux.Vars(r)
	vmId := vars["vmid"]

	obj := make(map[string]interface{})
	obj["actions"] = []tools.ActionBlock{{
		Action:  "stop",
		Actor:   "vm",
		Service: vmId,
		Force:   true,
	}}

	run, err := tools.ExecuteBlueprint(api.AysRepo, "vm", vmId, "delete", obj)
	if err != nil {
		log.Errorf("Error executing blueprint for vm %s deletion : %+v", vmId, err)
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	if err := tools.WaitRunDone(run.Key, api.AysRepo); err != nil {
		log.Errorf("Error while waiting for vm %s deletion : %+v", vmId, err)
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	res, err := api.AysAPI.Ays.DeleteServiceByName(vmId, "vm", api.AysRepo, nil, nil)
	if !tools.HandleAYSResponse(err, res, w, "deleting vm") {
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
