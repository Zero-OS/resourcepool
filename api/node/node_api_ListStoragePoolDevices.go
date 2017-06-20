package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// ListStoragePoolDevices is the handler for GET /nodes/{nodeid}/storagepools/{storagepoolname}/devices
// Lists the devices in the storage pool
func (api NodeAPI) ListStoragePoolDevices(w http.ResponseWriter, r *http.Request) {
	var respBody []StoragePoolDevice

	vars := mux.Vars(r)
	storagePoolName := vars["storagepoolname"]
	nodeId := vars["nodeid"]

	devices, err := api.getStoragePoolDevices(nodeId, storagePoolName, w, r)
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
func (api NodeAPI) getStoragePoolDevices(node, storagePool string, w http.ResponseWriter, r *http.Request) ([]DeviceInfo, bool) {
	aysClient := tools.GetAysConnection(r, api)
	queryParams := map[string]interface{}{"parent": fmt.Sprintf("node.zero-os!%s", node)}

	service, res, err := aysClient.Ays.GetServiceByName(storagePool, "storagepool", api.AysRepo, nil, queryParams)
	if !tools.HandleAYSResponse(err, res, w, "Getting storagepool service") {
		return nil, true
	}

	var data struct {
		Devices []DeviceInfo `json:"devices"`
	}

	if err := json.Unmarshal(service.Data, &data); err != nil {
		errMessage := fmt.Sprintf("Error Unmarshal storagepool service '%s'", storagePool)
		tools.WriteError(w, http.StatusInternalServerError, err, errMessage)
		return nil, true
	}

	return data.Devices, false
}
