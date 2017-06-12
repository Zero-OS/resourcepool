package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/gorilla/mux"
	runs "github.com/zero-os/0-orchestrator/api/run"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// CreateSnapshot is the handler for POST /nodes/{nodeid}/storagepools/{storagepoolname}/filesystem/{filesystemname}/snapshot
// Create a new readonly filesystem of the current state of the vdisk
func (api NodeAPI) CreateSnapshot(w http.ResponseWriter, r *http.Request) {
	filessytem := mux.Vars(r)["filesystemname"]
	nodeid := mux.Vars(r)["nodeid"]
	storagepool := mux.Vars(r)["storagepoolname"]

	var reqBody SnapShotCreate

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

	run, err := tools.ExecuteBlueprint(api.AysRepo, "fssnapshot", reqBody.Name, "install", blueprint)
	if err != nil {
		httpErr := err.(tools.HTTPError)
		errmsg := "Error executing blueprint for fssnapshot creation "
		tools.WriteError(w, httpErr.Resp.StatusCode, httpErr, errmsg)
	}

	response := runs.Run{Runid: run.Key, State: run.State}

	w.Header().Set("Location", fmt.Sprintf("/nodes/%s/storagepools/%s/filesystems/%s/snapshots/%s", nodeid, storagepool, filessytem, reqBody.Name))
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusAccepted)
	json.NewEncoder(w).Encode(&response)
}
