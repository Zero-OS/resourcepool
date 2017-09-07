package backup

import (
	"encoding/json"
	"github.com/zero-os/0-orchestrator/api/tools"
	"net/http"
)

type Backup struct {
	Name     string      `json:"name"`
	Snaphost string      `json:"snapshot"`
	URL      string      `json:"url"`
	Type     string      `json:"type"`
	Meta     interface{} `json:"meta"`
}

// List is the handler for GET /backup
// List backups
func (api BackupAPI) List(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)
	services, res, err := aysClient.Ays.ListServicesByRole("backup", api.AysRepo, nil, nil)
	if !tools.HandleAYSResponse(err, res, w, "listing container_backup") {
		return
	}

	var respBody = make([]Backup, len(services))
	for i, serviceData := range services {
		service, res, err := aysClient.Ays.GetServiceByName(serviceData.Name, serviceData.Role, api.AysRepo, nil, nil)
		if !tools.HandleAYSResponse(err, res, w, "Getting container backup service") {
			return
		}
		var data Backup
		if err := json.Unmarshal(service.Data, &data); err != nil {
			tools.WriteError(w, http.StatusInternalServerError, err, "Error unmarshaling ays response")
			return
		}
		data.Name = service.Name
		switch meta := data.Meta.(type) {
		case string:
			var obj interface{}
			if err := json.Unmarshal([]byte(meta), &obj); err == nil {
				data.Meta = obj
			}
		}
		respBody[i] = data
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
