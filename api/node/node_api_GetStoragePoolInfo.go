package node

import (
	"encoding/json"
	"net/http"

	log "github.com/Sirupsen/logrus"
	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// GetStoragePoolInfo is the handler for GET /nodes/{nodeid}/storagepools/{storagepoolname}
// Get detailed information of this storage pool
func (api *NodeAPI) GetStoragePoolInfo(w http.ResponseWriter, r *http.Request) {
	name := mux.Vars(r)["storagepoolname"]

	schema, err := api.getStoragepoolDetail(name, r)
	if err != nil {
		errmsg := "Error get info about storagepool services"

		if httpErr, ok := err.(tools.HTTPError); ok {
			tools.WriteError(w, httpErr.Resp.StatusCode, httpErr, errmsg)
			return
		}

		tools.WriteError(w, http.StatusInternalServerError, err, errmsg)
		return
	}
	respBody := StoragePool{
		Capacity:        schema.FreeCapacity,
		DataProfile:     schema.DataProfile,
		MetadataProfile: schema.MetadataProfile,
		Mountpoint:      schema.Mountpoint,
		Name:            name,
		Status:          schema.Status,
		TotalCapacity:   schema.TotalCapacity,
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}

type storagePoolSchema struct {
	DataProfile     EnumStoragePoolDataProfile     `json:"dataProfile"`
	MetadataProfile EnumStoragePoolMetadataProfile `json:"metadataProfile"`
	Status          EnumStoragePoolStatus          `json:"status"`
	FreeCapacity    uint64                         `json:"freeCapacity"`
	Mountpoint      string                         `json:"mountpoint" validate:"nonzero"`
	TotalCapacity   uint64                         `json:"totalCapacity"`
}

func (api *NodeAPI) getStoragepoolDetail(name string, r *http.Request) (*storagePoolSchema, error) {
	aysClient := tools.GetAysConnection(r, api)
	log.Debugf("Get schema detail for storagepool %s\n", name)

	service, resp, err := aysClient.Ays.GetServiceByName(name, "storagepool", api.AysRepo, nil, nil)
	if err != nil {
		return nil, tools.NewHTTPError(resp, err.Error())
	}

	if resp.StatusCode != http.StatusOK {
		return nil, tools.NewHTTPError(resp, resp.Status)
	}

	schema := storagePoolSchema{}
	if err := json.Unmarshal(service.Data, &schema); err != nil {
		return nil, err
	}

	return &schema, nil
}
