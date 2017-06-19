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
func (api NodeAPI) DeleteVM(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)
	vars := mux.Vars(r)
	vmId := vars["vmid"]

	obj := make(map[string]interface{})
	obj["actions"] = []tools.ActionBlock{{
		Action:  "stop",
		Actor:   "vm",
		Service: vmId,
		Force:   true,
	}}

	run, err := aysClient.ExecuteBlueprint(api.AysRepo, "vm", vmId, "delete", obj)
	if err != nil {
		httpErr := err.(tools.HTTPError)
		errmsg := fmt.Sprintf("error executing blueprint for vm %s deletion ", vmId)
		if httpErr.Resp.StatusCode/100 == 4 {
			tools.WriteError(w, httpErr.Resp.StatusCode, err, err.Error())
			return
		}
		tools.WriteError(w, httpErr.Resp.StatusCode, err, errmsg)
		return
	}

	if err := aysClient.WaitRunDone(run.Key, api.AysRepo); err != nil {
		errmsg := fmt.Sprintf("Error while waiting for vm %s deletion", vmId)
		tools.WriteError(w, http.StatusInternalServerError, err, errmsg)
		return
	}

	res, err := aysClient.Ays.DeleteServiceByName(vmId, "vm", api.AysRepo, nil, nil)
	if !tools.HandleAYSResponse(err, res, w, "deleting vm") {
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
