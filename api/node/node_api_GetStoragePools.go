package node

import (
	"encoding/json"
	"net/http"
)

// GetStoragePools is the handler for GET /node/{nodeid}/storagepool
// List storage pools present in the node
func (api NodeAPI) GetStoragePools(w http.ResponseWriter, r *http.Request) {
	var respBody []StoragePoolListItem
	json.NewEncoder(w).Encode(&respBody)
}
