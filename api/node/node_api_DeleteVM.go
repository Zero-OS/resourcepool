package node

import (
	"fmt"

	"net/http"

	"github.com/gorilla/mux"

	tools "github.com/zero-os/0-orchestrator/api/tools"
	//"fmt"
)

// DeleteVM is the handler for DELETE /nodes/{nodeid}/vms/{vmid}
// Deletes the VM
func (api *NodeAPI) DeleteVM(w http.ResponseWriter, r *http.Request) {
	aysClient, err := tools.GetAysConnection(api)
	if err != nil {
		tools.WriteError(w, http.StatusUnauthorized, err, "")
		return
	}
	vars := mux.Vars(r)
	vmID := vars["vmid"]

	obj := make(map[string]interface{})
	obj["actions"] = []tools.ActionBlock{{
		Action:  "destroy",
		Actor:   "vm",
		Service: vmID,
		Force:   true,
	}}

	run, err := aysClient.ExecuteBlueprint(api.AysRepo, "vm", vmID, "delete", obj)
	errmsg := fmt.Sprintf("error executing blueprint for vm %s deletion ", vmID)
	if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
		return
	}

	if _, err := aysClient.WaitRunDone(run.Key, api.AysRepo); err != nil {
		errmsg := fmt.Sprintf("Error while waiting for vm %s deletion", vmID)
		tools.WriteError(w, http.StatusInternalServerError, err, errmsg)
		return
	}

	res, err := aysClient.Ays.DeleteServiceByName(vmID, "vm", api.AysRepo, nil, nil)
	if !tools.HandleAYSDeleteResponse(err, res, w, "deleting vm") {
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
