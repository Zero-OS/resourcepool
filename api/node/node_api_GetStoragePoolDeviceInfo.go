package node

import (
	"encoding/json"
	"net/http"

	"github.com/gorilla/mux"
)

// GetStoragePoolDeviceInfo is the handler for GET /nodes/{nodeid}/storagepools/{storagepoolname}/device/{deviceuuid}
// Get information of the device
func (api NodeAPI) GetStoragePoolDeviceInfo(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	storagePoolName := vars["storagepoolname"]
	nodeId := vars["nodeid"]
	deviceUuid := vars["deviceuuid"]

	devices, err := api.getStoragePoolDevices(nodeId, storagePoolName, w)
	if err {
		return
	}

	for _, device := range devices {
		if device.PartUUID == deviceUuid {
			respBody := StoragePoolDevice{UUID: device.PartUUID, DeviceName: device.Device, Status: device.Status}
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusOK)
			json.NewEncoder(w).Encode(&respBody)
			return
		}
	}

	w.WriteHeader(http.StatusNotFound)
}
