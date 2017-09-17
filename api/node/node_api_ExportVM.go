package node

import (
	"encoding/json"
	"fmt"
	"net/http"
	"time"

	"github.com/gorilla/mux"

	tools "github.com/zero-os/0-orchestrator/api/tools"
)

// ExportVM is the handler for POST /nodes/{nodeid}/vms/{vmid}/export
// Creates the VM
func (api NodeAPI) ExportVM(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)

	vars := mux.Vars(r)
	vmID := vars["vmid"]

	var reqBody ExportVM

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err, "Error decoding request body")
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	// valdiate name
	exists, err := aysClient.ServiceExists("vm", vmID, api.AysRepo)
	if !exists {
		err = fmt.Errorf("VM with name %s does not exist", vmID)
		tools.WriteError(w, http.StatusNotFound, err, err.Error())
		return
	}

	now := time.Now()
	bp := struct {
		URL string `yaml:"backupUrl" json:"backupUrl"`
	}{
		URL: fmt.Sprintf("%s#%s_%v", reqBody.URL, vmID, now.Unix()),
	}

	obj := make(map[string]interface{})
	obj[fmt.Sprintf("vm__%s", vmID)] = bp

	res, err := aysClient.ExecuteBlueprint(api.AysRepo, "vm", vmID, "export", obj)
	errmsg := fmt.Sprintf("error executing blueprint for vm %s export", vmID)
	if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
		return
	}

	if _, err := aysClient.WaitRunDone(res.Key, api.AysRepo); err != nil {
		httpErr, ok := err.(tools.HTTPError)
		if ok {
			tools.WriteError(w, httpErr.Resp.StatusCode, httpErr, "")
		} else {
			tools.WriteError(w, http.StatusInternalServerError, err, errmsg)
		}
		return
	}
	w.WriteHeader(http.StatusOK)
}
