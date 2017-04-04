package node

import (
	"net/http"
)

// DeleteStoragePoolDevice is the handler for DELETE /node/{nodeid}/storagepool/{storagepoolname}/device/{deviceuuid}
// Removes the device from the storagepool
func (api NodeAPI) DeleteStoragePoolDevice(w http.ResponseWriter, r *http.Request) {
}
