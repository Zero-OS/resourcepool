package node

import (
	"encoding/json"
	"net/http"
)

// CreateStoragePoolDevices is the handler for POST /node/{nodeid}/storagepool/{storagepoolname}/device
// Add extra devices to this storage pool
func (api NodeAPI) CreateStoragePoolDevices(w http.ResponseWriter, r *http.Request) {
	var reqBody []string

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		w.WriteHeader(400)
		return
	}
}
