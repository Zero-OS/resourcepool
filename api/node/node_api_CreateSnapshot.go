package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/gorilla/mux"

	"github.com/zero-os/0-orchestrator/api/httperror"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// CreateSnapshot is the handler for POST /nodes/{nodeid}/storagepools/{storagepoolname}/filesystem/{filesystemname}/snapshot
// Create a new readonly filesystem of the current state of the vdisk
func (api *NodeAPI) CreateSnapshot(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)
	filessytem := mux.Vars(r)["filesystemname"]
	nodeid := mux.Vars(r)["nodeid"]
	storagepool := mux.Vars(r)["storagepoolname"]

	var reqBody SnapShotCreate

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		httperror.WriteError(w, http.StatusBadRequest, err, "Error decoding request body")
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		httperror.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	bpContent := struct {
		Filesystem string `yaml:"filesystem" json:"filesystem"`
		Name       string `yaml:"name" json:"name"`
	}{

		Filesystem: filessytem,
		Name:       reqBody.Name,
	}

	blueprint := map[string]interface{}{
		fmt.Sprintf("fssnapshot__%s", reqBody.Name): bpContent,
		"actions": []tools.ActionBlock{{
			Action:  "install",
			Actor:   "fssnapshot",
			Service: reqBody.Name}},
	}

	run, err := aysClient.ExecuteBlueprint(api.AysRepo, "fssnapshot", reqBody.Name, "install", blueprint)
	errmsg := "Error executing blueprint for fssnapshot creation "
	if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
		return
	}

	if _, errr := aysClient.WaitOnRun(w, api.AysRepo, run.Key); errr != nil {
		return
	}
	w.Header().Set("Location", fmt.Sprintf("/nodes/%s/storagepools/%s/filesystems/%s/snapshots/%s", nodeid, storagepool, filessytem, reqBody.Name))
	w.WriteHeader(http.StatusCreated)

}
