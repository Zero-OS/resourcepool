package backup

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/gorilla/mux"

	"github.com/zero-os/0-orchestrator/api/tools"
)

// CreateContainer is the handler for POST /backup
// Create a new Container
func (api BackupAPI) Create(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)
	var reqBody BackupContainer

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	vars := mux.Vars(r)
	containerName := vars["containername"]

	// validate container name
	exists, err := aysClient.ServiceExists("container", containerName, api.AysRepo)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "Error checking container service exists")
		return
	} else if !exists {
		err = fmt.Errorf("Container with name %s does not exists", containerName)
		tools.WriteError(w, http.StatusNotFound, err, "")
		return
	}

	bp := map[string]interface{}{
		fmt.Sprintf("container_backup__%s", reqBody.Name): map[string]interface{}{
			"container": containerName,
			"url":       reqBody.URL,
		},
		"actions": []tools.ActionBlock{
			{Action: "install", Service: reqBody.Name, Actor: "container_backup"},
		},
	}

	run, err := aysClient.ExecuteBlueprint(api.AysRepo, "container_backup", reqBody.Name, "install", bp)
	errmsg := fmt.Sprintf("error executing blueprint for container %s creation", reqBody.Name)
	if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
		return
	}

	if _, errr := tools.WaitOnRun(api, w, r, run.Key); errr != nil {
		return
	}
	w.Header().Set("Location", fmt.Sprintf("/backup/%s", reqBody.Name))
	w.WriteHeader(http.StatusCreated)
}
