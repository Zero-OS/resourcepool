package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/gorilla/mux"
	runs "github.com/zero-os/0-orchestrator/api/run"
	tools "github.com/zero-os/0-orchestrator/api/tools"
)

// CreateVM is the handler for POST /nodes/{nodeid}/vms
// Creates the VM
func (api NodeAPI) CreateVM(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)
	var reqBody VMCreate

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
	exists, err := aysClient.ServiceExists("vm", reqBody.Id, api.AysRepo)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "Failed to check for conflicting services")
		return
	}
	if exists {
		err = fmt.Errorf("VM with name %s already exists", reqBody.Id)
		tools.WriteError(w, http.StatusConflict, err, err.Error())
		return
	}

	vars := mux.Vars(r)
	nodeid := vars["nodeid"]

	// Create blueprint
	bp := struct {
		Node   string      `yaml:"node" json:"node"`
		Memory int         `yaml:"memory" json:"memory"`
		CPU    int         `yaml:"cpu" json:"cpu"`
		Nics   []NicLink   `yaml:"nics" json:"nics"`
		Disks  []VDiskLink `yaml:"disks" json:"disks"`
	}{
		Node:   nodeid,
		Memory: reqBody.Memory,
		CPU:    reqBody.Cpu,
		Nics:   reqBody.Nics,
		Disks:  reqBody.Disks,
	}

	obj := make(map[string]interface{})
	obj[fmt.Sprintf("vm__%s", reqBody.Id)] = bp
	obj["actions"] = []tools.ActionBlock{{Service: reqBody.Id, Actor: "vm", Action: "install"}}

	run, err := aysClient.ExecuteBlueprint(api.AysRepo, "vm", reqBody.Id, "install", obj)
	if err != nil {
		httpErr := err.(tools.HTTPError)
		errmsg := fmt.Sprintf("error executing blueprint for vm %s creation", reqBody.Id)
		tools.WriteError(w, httpErr.Resp.StatusCode, err, errmsg)
		return
	}

	response := runs.Run{Runid: run.Key, State: runs.EnumRunState(run.State)}

	w.Header().Set("Location", fmt.Sprintf("/nodes/%s/vms/%s", nodeid, reqBody.Id))
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusAccepted)
	json.NewEncoder(w).Encode(&response)

}
