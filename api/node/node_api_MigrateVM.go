package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	log "github.com/Sirupsen/logrus"
	"github.com/g8os/resourcepool/api/tools"
	"github.com/gorilla/mux"
)

// MigrateVM is the handler for POST /nodes/{nodeid}/vms/{vmid}/migrate
// Migrate the VM to another host
func (api NodeAPI) MigrateVM(w http.ResponseWriter, r *http.Request) {
	var reqBody VMMigrate

	vmID := mux.Vars(r)["vmid"]

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		w.WriteHeader(400)
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		w.WriteHeader(400)
		w.Write([]byte(`{"error":"` + err.Error() + `"}`))
		return
	}

	// Create migrate blueprint
	bp := struct {
		Node string `yaml:"node" json:"node"`
	}{
		Node: reqBody.Nodeid,
	}

	decl := fmt.Sprintf("vm__%v", vmID)

	obj := make(map[string]interface{})
	obj[decl] = bp
	obj["actions"] = []tools.ActionBlock{{
		Action:  "migrate",
		Actor:   "vm",
		Service: vmID,
		Force:   true,
	}}

	// And execute
	if _, err := tools.ExecuteBlueprint(api.AysRepo, "vm", vmID, "migrate", obj); err != nil {
		log.Errorf("error executing blueprint for vm %s migrate : %+v", vmID, err)
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
