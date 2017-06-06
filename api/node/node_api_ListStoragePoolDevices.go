package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	log "github.com/Sirupsen/logrus"
	"github.com/zero-os/0-orchestrator/api/tools"
	"github.com/gorilla/mux"
)

// ListStoragePoolDevices is the handler for GET /nodes/{nodeid}/storagepools/{storagepoolname}/devices
// Lists the devices in the storage pool
func (api NodeAPI) ListStoragePoolDevices(w http.ResponseWriter, r *http.Request) {
	var respBody []StoragePoolDevice

	vars := mux.Vars(r)
	storagePoolName := vars["storagepoolname"]
	nodeId := vars["nodeid"]

	devices, err := api.getStoragePoolDevices(nodeId, storagePoolName, w)
	if err {
		return
	}

	for _, device := range devices {
		respBody = append(respBody, StoragePoolDevice{
			UUID:       device.PartUUID,
			DeviceName: device.Device,
			Status:     device.Status})
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}

type DeviceInfo struct {
	Device   string                      `json:"device"`
	PartUUID string                      `json:"partUUID"`
	Status   EnumStoragePoolDeviceStatus `json:"status"`
}

// Get storagepool devices
func (api NodeAPI) getStoragePoolDevices(node, storagePool string, w http.ResponseWriter) ([]DeviceInfo, bool) {
	queryParams := map[string]interface{}{"parent": fmt.Sprintf("node.zero-os!%s", node)}

	service, res, err := api.AysAPI.Ays.GetServiceByName(storagePool, "storagepool", api.AysRepo, nil, queryParams)
	if !tools.HandleAYSResponse(err, res, w, "Getting storagepool service") {
		return nil, true
	}

	var data struct {
		Devices []DeviceInfo `json:"devices"`
	}

	if err := json.Unmarshal(service.Data, &data); err != nil {
		errMessage := fmt.Errorf("Error Unmarshal storagepool service '%s' data: %+v", storagePool, err)
		log.Error(errMessage)
		tools.WriteError(w, http.StatusInternalServerError, errMessage)
		return nil, true
	}

	return data.Devices, false
}
