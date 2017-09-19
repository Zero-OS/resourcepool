package node

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strings"
	"time"

	"github.com/gorilla/mux"

	"github.com/zero-os/0-orchestrator/api/httperror"
	tools "github.com/zero-os/0-orchestrator/api/tools"
)

// ExportVM is the handler for POST /nodes/{nodeid}/vms/{vmid}/export
// Creates the VM
func (api *NodeAPI) ExportVM(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)

	vars := mux.Vars(r)
	vmID := vars["vmid"]

	var reqBody ExportVM

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		httperror.WriteError(w, http.StatusBadRequest, err, "Error decoding request body")
		return
	}

	// Check if vm running
	srv, getres, err := aysClient.Ays.GetServiceByName(vmID, "vm", api.AysRepo, nil, nil)
	if !tools.HandleAYSResponse(err, getres, w, fmt.Sprintf("getting vm %s details", vmID)) {
		return
	}
	var vm VM
	if err := json.Unmarshal(srv.Data, &vm); err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Error unmarshaling ays response")
		return
	}

	if vm.Status != EnumVMStatushalted {
		err = fmt.Errorf("VM %s must be halted before export", vmID)
		httperror.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	// validate request
	reqBody.URL = strings.TrimRight(reqBody.URL, "/")
	if err := reqBody.Validate(); err != nil {
		httperror.WriteError(w, http.StatusBadRequest, err, "")
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

	_, err = aysClient.UpdateBlueprint(api.AysRepo, "vm", vmID, "export", obj)
	errmsg := fmt.Sprintf("error executing blueprint for vm %s export", vmID)
	if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
		return
	}

	respBody := struct {
		BackupURL string `yaml:"url" json:"url"`
	}{
		BackupURL: strings.Replace(bp.URL, "#", "/", 1),
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)

}
