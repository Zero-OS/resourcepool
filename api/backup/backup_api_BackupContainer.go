package backup

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/zero-os/0-orchestrator/api/ays"

	"github.com/zero-os/0-orchestrator/api/httperror"
)

// Create is the handler for POST /backup
// Create a backup
func (api *BackupAPI) Create(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)
	var reqBody BackupContainer

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		httperror.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		httperror.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	// validate container name
	exists, err := api.client.IsServiceExists("container", reqBody.Container)
	if err != nil {
		err.Handle(w, http.StatusInternalServerError)
		return
	}

	if !exists {
		err := fmt.Errorf("container with name %s does not exists", reqBody.Container)
		httperror.WriteError(w, http.StatusNotFound, err, err.Error())
	}
	// if exists, err := aysClient.ServiceExists("container", reqBody.Container, api.AysRepo); err != nil {
	// 	httperror.WriteError(w, http.StatusInternalServerError, err, "Error checking container service exists")
	// 	return
	// } else if !exists {
	// 	err = fmt.Errorf("container with name %s does not exists", reqBody.Container)
	// 	httperror.WriteError(w, http.StatusNotFound, err, "")
	// 	return
	// }

	// validate container name
	// validate container name
	exists, err = api.client.IsServiceExists("container_backup", reqBody.Container)
	if err != nil {
		err.Handle(w, http.StatusInternalServerError)
		return
	}

	if !exists {
		err := fmt.Errorf("container backup with name %s does not exists", reqBody.Container)
		httperror.WriteError(w, http.StatusNotFound, err, err.Error())
	}
	// if exists, err := aysClient.ServiceExists("container_backup", reqBody.Name, api.AysRepo); err != nil {
	// 	httperror.WriteError(w, http.StatusInternalServerError, err, "Error checking container backup service exists")
	// 	return
	// } else if exists {
	// 	err = fmt.Errorf("container backup with name %s already exists", reqBody.Name)
	// 	httperror.WriteError(w, http.StatusNotFound, err, "")
	// 	return
	// }

	bp := ays.Blueprint{
		fmt.Sprintf("backup.container__%s", reqBody.Name): map[string]interface{}{
			"container": reqBody.Container,
			"url":       reqBody.URL,
		},
		"actions": []ays.ActionBlock{
			{Action: "install", Service: reqBody.Name, Actor: "backup.container"},
		},
	}
	bpName := ays.BlueprintName("container_backup", reqBody.Name, "install")
	if _, err := api.client.CreateExecRun(bpName, bp, true); err != nil {
		if aysErr, ok := err.(*ays.Error); ok {
			aysErr.Handle(w, http.StatusInternalServerError)
		} else {
			httperror.WriteError(w, http.StatusInternalServerError, err, err.Error())
		}
		return
	}
	// run, err := aysClient.ExecuteBlueprint(api.AysRepo, "container_backup", reqBody.Name, "install", bp)
	// errmsg := fmt.Sprintf("error executing blueprint for container %s creation", reqBody.Name)
	// if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
	// 	return
	// }

	// if _, errr := aysClient.WaitOnRun(w, api.AysRepo, run.Key); errr != nil {
	// 	return
	// }

	w.Header().Set("Location", fmt.Sprintf("/backup/%s", reqBody.Name))
	w.WriteHeader(http.StatusCreated)
}
