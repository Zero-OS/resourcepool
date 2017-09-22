package node

import (
	"net/http"

	"github.com/gorilla/mux"

	"github.com/zero-os/0-orchestrator/api/ays"
	"github.com/zero-os/0-orchestrator/api/handlers"
	tools "github.com/zero-os/0-orchestrator/api/tools"
	//"fmt"
)

// DeleteVM is the handler for DELETE /nodes/{nodeid}/vms/{vmid}
// Deletes the VM
func (api *NodeAPI) DeleteVM(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)
	vars := mux.Vars(r)
	vmId := vars["vmid"]

	obj := ays.Blueprint{
		"actions": []tools.ActionBlock{{
			Action:  "destroy",
			Actor:   "vm",
			Service: vmId,
			Force:   true,
		}},
	}
	// obj["actions"] = []tools.ActionBlock{{
	// 	Action:  "destroy",
	// 	Actor:   "vm",
	// 	Service: vmId,
	// 	Force:   true,
	// }}

	// run, err := aysClient.ExecuteBlueprint(api.AysRepo, "vm", vmId, "delete", obj)
	// errmsg := fmt.Sprintf("error executing blueprint for vm %s deletion ", vmId)
	// if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
	// 	return
	// }

	// if _, err := aysClient.WaitRunDone(run.Key, api.AysRepo); err != nil {
	// 	errmsg := fmt.Sprintf("Error while waiting for vm %s deletion", vmId)
	// 	httperror.WriteError(w, http.StatusInternalServerError, err, errmsg)
	// 	return
	// }

	bpName := ays.BlueprintName("vm", vmId, "delete")
	if _, err := api.client.CreateExecRun(bpName, bp); err != nil {
		handlers.HandleError(w, err)
		return
	}

	// res, err := aysClient.Ays.DeleteServiceByName(vmId, "vm", api.AysRepo, nil, nil)
	// if !tools.HandleAYSResponse(err, res, w, "deleting vm") {
	// 	return
	// }
	bpName := ays.BlueprintName("vm", vmId, "delete")
	if _, err := api.client.CreateExecRun(bpName, bp); err != nil {
		handlers.HandleError(w, err)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
