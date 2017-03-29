package main

import (
	"encoding/json"
	"net/http"
)

// GetStoragePoolDeviceInfo is the handler for GET /node/{nodeid}/storagepool/{storagepoolname}/device/{deviceuuid}
// Get information of the device
func (api NodeAPI) GetStoragePoolDeviceInfo(w http.ResponseWriter, r *http.Request) {
	var respBody StoragePoolDevice
	json.NewEncoder(w).Encode(&respBody)
}
