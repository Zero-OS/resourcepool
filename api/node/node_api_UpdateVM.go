package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	log "github.com/Sirupsen/logrus"
	tools "github.com/g8os/resourcepool/api/tools"
	"github.com/gorilla/mux"
)

// UpdateVM is the handler for PUT /nodes/{nodeid}/vms/{vmid}
// Updates the VM
func (api NodeAPI) UpdateVM(w http.ResponseWriter, r *http.Request) {
	var reqBody VMUpdate

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		w.WriteHeader(400)
		w.Write([]byte(`{"error":"` + err.Error() + `"}`))
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		w.WriteHeader(400)
		w.Write([]byte(`{"error":"` + err.Error() + `"}`))
		return
	}

	vars := mux.Vars(r)
	vmid := vars["vmid"]

	bp := struct {
		Memory int         `yaml:"memory" json:"memory"`
		CPU    int         `yaml:"cpu" json:"cpu"`
		Nics   []NicLink   `yaml:"nics" json:"nics"`
		Disks  []VDiskLink `yaml:"disks" json:"disks"`
	}{
		Memory: reqBody.Memory,
		CPU:    reqBody.Cpu,
		Nics:   reqBody.Nics,
		Disks:  reqBody.Disks,
	}

	obj := make(map[string]interface{})
	obj[fmt.Sprintf("vm__%s", vmid)] = bp

	if _, err := tools.ExecuteBlueprint(api.AysRepo, "vm", vmid, "update", obj); err != nil {
		log.Errorf("error executing blueprint for vm %s creation : %+v", vmid, err)
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
