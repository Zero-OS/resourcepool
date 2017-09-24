package node

import (
	"encoding/json"
	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/handlers"

	log "github.com/Sirupsen/logrus"
)

// GetFilesystemInfo is the handler for GET /nodes/{nodeid}/storagepools/{storagepoolname}/filesystem/{filesystemname}
// Get detailed filesystem information
func (api *NodeAPI) GetFilesystemInfo(w http.ResponseWriter, r *http.Request) {

	storagepool := mux.Vars(r)["storagepoolname"]
	name := mux.Vars(r)["filesystemname"]

	schema, err := api.getFilesystemDetail(name)
	if err != nil {
		handlers.HandleError(w, err)
		return
		// errmsg := "Error get info about filesystem services"

		// if httpErr, ok := err.(httperror.HTTPError); ok {
		// 	httperror.WriteError(w, httpErr.Resp.StatusCode, httpErr, errmsg)
		// 	return
		// }

		// httperror.WriteError(w, http.StatusInternalServerError, err, errmsg)
		// return
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

func (api *NodeAPI) getFilesystemDetail(name string) (*FilesystemSchema, error) {
	// aysClient := tools.GetAysConnection(r, api)
	log.Debugf("Get schema detail for filesystem %s\n", name)

	// service, resp, err := aysClient.Ays.GetServiceByName(name, "filesystem", api.AysRepo, nil, nil)
	// if err != nil {
	// 	return nil, httperror.New(resp, err.Error())
	// }
	service, err := api.client.GetService("filesystem", name, "", nil)
	if err != nil {
		return nil, err
	}

	// if resp.StatusCode != http.StatusOK {
	// 	return nil, httperror.New(resp, resp.Status)
	// }

	schema := FilesystemSchema{}
	if err := json.Unmarshal(service.Data, &schema); err != nil {
		return nil, err
	}

	return &schema, nil
}
