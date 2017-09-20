package node

import (
	"encoding/json"
	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"

	log "github.com/Sirupsen/logrus"
)

// GetFilesystemInfo is the handler for GET /nodes/{nodeid}/storagepools/{storagepoolname}/filesystem/{filesystemname}
// Get detailed filesystem information
func (api *NodeAPI) GetFilesystemInfo(w http.ResponseWriter, r *http.Request) {

	storagepool := mux.Vars(r)["storagepoolname"]
	name := mux.Vars(r)["filesystemname"]

	schema, err := api.getFilesystemDetail(name, r)
	if err != nil {
		errmsg := "Error get info about filesystem services"

		if httpErr, ok := err.(tools.HTTPError); ok {
			tools.WriteError(w, httpErr.Resp.StatusCode, httpErr, errmsg)
			return
		}

		tools.WriteError(w, http.StatusInternalServerError, err, errmsg)
		return
	}

	respBody := Filesystem{
		Mountpoint: schema.Mountpoint,
		Name:       name,
		Parent:     storagepool,
		Quota:      schema.Quota,
		ReadOnly:   schema.ReadOnly,
		SizeOnDisk: schema.SizeOnDisk,
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}

type FilesystemSchema struct {
	Mountpoint  string `json:"mountpoint"`
	Name        string `json:"name"`
	Quota       int    `json:"quota"`
	ReadOnly    bool   `json:"readOnly"`
	SizeOnDisk  int    `json:"sizeOnDisk"`
	StoragePool string `json:"storagePool"`
}

func (api *NodeAPI) getFilesystemDetail(name string, r *http.Request) (*FilesystemSchema, error) {
	aysClient := tools.GetAysConnection(r, api)
	log.Debugf("Get schema detail for filesystem %s\n", name)

	service, resp, err := aysClient.Ays.GetServiceByName(name, "filesystem", api.AysRepo, nil, nil)
	if err != nil {
		return nil, tools.NewHTTPError(resp, err.Error())
	}

	if resp.StatusCode != http.StatusOK {
		return nil, tools.NewHTTPError(resp, resp.Status)
	}

	schema := FilesystemSchema{}
	if err := json.Unmarshal(service.Data, &schema); err != nil {
		return nil, err
	}

	return &schema, nil
}
