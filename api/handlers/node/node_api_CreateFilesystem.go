package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/gorilla/mux"

	"github.com/zero-os/0-orchestrator/api/ays"
	"github.com/zero-os/0-orchestrator/api/handlers"
	"github.com/zero-os/0-orchestrator/api/httperror"
)

// CreateFilesystem is the handler for POST /nodes/{nodeid}/storagepools/{storagepoolname}/filesystem
// Create a new filesystem
func (api *NodeAPI) CreateFilesystem(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)
	var reqBody FilesystemCreate
	nodeid := mux.Vars(r)["nodeid"]
	storagepool := mux.Vars(r)["storagepoolname"]

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

	filesystem := struct {
		Name        string `yaml:"name" json:"name"`
		Quota       uint32 `yaml:"quota" json:"quota"`
		ReadOnly    bool   `yaml:"readOnly" json:"readOnly"`
		StoragePool string `json:"storagePool" yaml:"storagePool"`
	}{
		Name:        reqBody.Name,
		Quota:       reqBody.Quota,
		ReadOnly:    reqBody.ReadOnly,
		StoragePool: storagepool,
	}

	// blueprint := map[string]interface{}{
	// 	fmt.Sprintf("filesystem__%s", reqBody.Name): bpContent,
	// 	"actions": []tools.ActionBlock{{Action: "install", Service: reqBody.Name, Actor: "filesystem"}},
	// }

	// run, err := aysClient.ExecuteBlueprint(api.AysRepo, "filesystem", reqBody.Name, "install", blueprint)
	// errmsg := "Error executing blueprint for filesystem creation "
	// if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
	// 	return
	// }

	// if _, errr := aysClient.WaitOnRun(w, api.AysRepo, run.Key); errr != nil {
	// 	return
	// }

	serviceName := fmt.Sprintf("filesystem__%s", reqBody.Name)
	blueprint := ays.Blueprint{
		serviceName: filesystem,
		"actions": []ays.ActionBlock{{
			Action:  "install",
			Actor:   "filesystem",
			Service: reqBody.Name,
		}},
	}
	blueprintName := ays.BlueprintName("filesystem", reqBody.Name, "create")
	if _, err := api.client.CreateExecRun(blueprintName, blueprint, true); err != nil {
		handlers.HandleError(w, err)
		return
	}

	w.Header().Set("Location", fmt.Sprintf("/nodes/%s/storagepools/%s/filesystems/%s", nodeid, storagepool, reqBody.Name))
	w.WriteHeader(http.StatusCreated)

}
