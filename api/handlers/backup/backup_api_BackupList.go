package backup

import (
	"encoding/json"
	"fmt"
	"net/http"
	"sync"

	"github.com/zero-os/0-orchestrator/api/ays"
	"github.com/zero-os/0-orchestrator/api/httperror"

	"github.com/siddontang/go/log"
	"github.com/zero-os/0-orchestrator/api/ays/ays-client"
)

type backup struct {
	Name     string      `json:"name"`
	Snaphost string      `json:"snapshot"`
	URL      string      `json:"url"`
	Type     string      `json:"type"`
	Meta     interface{} `json:"meta"`
}

// List is the handler for GET /backup
// List backups
func (api *BackupAPI) List(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)

	services, err := api.client.ListServices("backup")
	if err != nil {
		err.Handle(w, http.StatusInternalServerError)
		return
	}
	// services, res, err := aysClient.Ays.ListServicesByRole("backup", api.AysRepo, nil, nil)
	// if !tools.HandleAYSResponse(err, res, w, "listing container_backup") {
	// 	return
	// }

	var (
		wg       sync.WaitGroup
		respBody = make([]*backup, len(services))
		errs     = make([]error, len(services))
	)

	wg.Add(len(services))

	for i, serviceData := range services {
		go func(i int, serviceData *client.ServiceData) {

			defer wg.Done()
			backup, err := api.getBackup(serviceData)
			if err != nil {
				log.Errorf("error retrieving backup service: %v", err)
				errs[i] = err
				return
			}

			respBody[i] = backup
		}(i, serviceData)
		// service, res, err := aysClient.Ays.GetServiceByName(serviceData.Name, serviceData.Role, api.AysRepo, nil, nil)
		// if !tools.HandleAYSResponse(err, res, w, "Getting container backup service") {
		// 	return
		// }
		// var data Backup
		// if err := json.Unmarshal(service.Data, &data); err != nil {
		// 	httperror.WriteError(w, http.StatusInternalServerError, err, "Error unmarshaling ays response")
		// 	return
		// }
		// data.Name = service.Name
		// switch meta := data.Meta.(type) {
		// case string:
		// 	var obj interface{}
		// 	if err := json.Unmarshal([]byte(meta), &obj); err == nil {
		// 		data.Meta = obj
		// 	}
		// }
		// respBody[i] = data
	}

	wg.Wait()

	for _, err := range errs {
		if err != nil {
			if aysErr, ok := err.(*ays.Error); ok {
				aysErr.Handle(w, http.StatusInternalServerError)
			} else {
				httperror.WriteError(w, http.StatusInternalServerError, err, err.Error())
			}
			return
		}
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}

func (api *BackupAPI) getBackup(serviceData *client.ServiceData) (*backup, error) {
	service, err := api.client.GetService(serviceData.Role, serviceData.Name, "", nil)
	if err != nil {
		return nil, err
	}

	var backup = &backup{}
	if err := json.Unmarshal(service.Data, backup); err != nil {
		return nil, fmt.Errorf("Error unmarshaling ays response: %v", err)
	}

	backup.Name = service.Name
	return backup, nil
}
