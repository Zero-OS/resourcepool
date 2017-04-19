package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/g8os/grid/api/tools"
	"github.com/gorilla/mux"

	log "github.com/Sirupsen/logrus"
)

// CreateSnapshot is the handler for POST /nodes/{nodeid}/storagepools/{storagepoolname}/filesystem/{filesystemname}/snapshot
// Create a new readonly filesystem of the current state of the vdisk
func (api NodeAPI) CreateSnapshot(w http.ResponseWriter, r *http.Request) {
	filessytem := mux.Vars(r)["filesystemname"]
	nodeid := mux.Vars(r)["nodeid"]
	storagepool := mux.Vars(r)["storagepoolname"]

	var name string

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&name); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err)
		return
	}

	bpContent := struct {
		Filesystem string `yaml:"filesystem" json:"filesystem"`
		Name       string `yaml:"name" json:"name"`
	}{

		Filesystem: filessytem,
		Name:       name,
	}

	blueprint := map[string]interface{}{
		fmt.Sprintf("fssnapshot__%s", name): bpContent,
		"actions":                           []tools.ActionBlock{{"action": "install"}},
	}

	if _, err := tools.ExecuteBlueprint(api.AysRepo, "fssnapshot", name, "install", blueprint); err != nil {
		httpErr := err.(tools.HTTPError)
		log.Errorf("Error executing blueprint for fssnapshot creation : %+v", err.Error())
		tools.WriteError(w, httpErr.Resp.StatusCode, httpErr)
	}
	w.Header().Set("Location", fmt.Sprintf("/nodes/%s/storagepools/%s/filesystems/%s/snapshots/%s", nodeid, storagepool, filessytem, name))
	w.WriteHeader(http.StatusCreated)
}
