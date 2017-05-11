package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	log "github.com/Sirupsen/logrus"
	tools "github.com/g8os/resourcepool/api/tools"
	"github.com/gorilla/mux"
)

// CreateVM is the handler for POST /nodes/{nodeid}/vms
// Creates the VM
func (api NodeAPI) CreateVM(w http.ResponseWriter, r *http.Request) {
	var reqBody VMCreate

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err)
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err)
		return
	}

	vars := mux.Vars(r)
	nodeid := vars["nodeid"]

	// Create blueprint
	userCloudInit, err := json.Marshal(reqBody.UserCloudInit)
	if err != nil {
		tools.WriteError(w, http.StatusBadRequest, err)
		return
	}
	systemCloudInit, err := json.Marshal(reqBody.SystemCloudInit)
	if err != nil {
		tools.WriteError(w, http.StatusBadRequest, err)
		return
	}
	bp := struct {
		Node            string      `yaml:"node" json:"node"`
		Memory          int         `yaml:"memory" json:"memory"`
		CPU             int         `yaml:"cpu" json:"cpu"`
		Nics            []NicLink   `yaml:"nics" json:"nics"`
		Disks           []VDiskLink `yaml:"disks" json:"disks"`
		UserCloudInit   string      `yaml:"userCloudInit" json:"userCloudInit"`
		SystemCloudInit string      `yaml:"systemCloudInit" json:"systemCloudInit"`
	}{
		Node:            nodeid,
		Memory:          reqBody.Memory,
		CPU:             reqBody.Cpu,
		Nics:            reqBody.Nics,
		Disks:           reqBody.Disks,
		UserCloudInit:   string(userCloudInit),
		SystemCloudInit: string(systemCloudInit),
	}

	obj := make(map[string]interface{})
	obj[fmt.Sprintf("vm__%s", reqBody.Id)] = bp
	obj["actions"] = []tools.ActionBlock{{Service: reqBody.Id, Actor: "vm", Action: "install"}}

	if _, err := tools.ExecuteBlueprint(api.AysRepo, "vm", reqBody.Id, "install", obj); err != nil {
		log.Errorf("error executing blueprint for vm %s creation : %+v", reqBody.Id, err)
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	w.Header().Set("Location", fmt.Sprintf("/nodes/%s/vms/%s", nodeid, reqBody.Id))
	w.WriteHeader(http.StatusCreated)
}
