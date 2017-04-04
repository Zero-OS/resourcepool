package node

import (
	"encoding/json"
	"net/http"
)

// ListStoragePoolDevices is the handler for GET /node/{nodeid}/storagepool/{storagepoolname}/device
// Lists the devices in the storage pool
func (api NodeAPI) ListStoragePoolDevices(w http.ResponseWriter, r *http.Request) {
	var respBody []StoragePoolDevice
	json.NewEncoder(w).Encode(&respBody)
}
