package node

import (
	"encoding/json"
	"fmt"
	"net/http"
	"time"

	"github.com/g8os/grid/api/tools"
	"github.com/gorilla/mux"

	log "github.com/Sirupsen/logrus"
)

// CreateSnapshot is the handler for POST /node/{nodeid}/storagepool/{storagepoolname}/filesystem/{filesystemname}/snapshot
// Create a new readonly filesystem of the current state of the volume
func (api NodeAPI) CreateSnapshot(w http.ResponseWriter, r *http.Request) {
	filessytem := mux.Vars(r)["filesystemname"]

	var name string

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&name); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err)
		return
	}

	bpContent := struct {
		Filesystem string `json:"filesystem"`
		Name       string `json:"name"`
	}{

		Filesystem: filessytem,
		Name:       name,
	}

	blueprint := map[string]interface{}{
		fmt.Sprintf("fssnapshot__%s", name): bpContent,
		"actions":                           []map[string]string{{"action": "install"}},
	}

	blueprintName := fmt.Sprintf("fssnaptshot__%s_create_%d", name, time.Now().Unix())

	if _, err := tools.ExecuteBlueprint(api.AysRepo, blueprintName, blueprint); err != nil {
		httpErr := err.(tools.HTTPError)
		log.Errorf("Error executing blueprint for fssnapshot creation : %+v", err.Error())
		tools.WriteError(w, httpErr.Resp.StatusCode, httpErr)
	}
}
