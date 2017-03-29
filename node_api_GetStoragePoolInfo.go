package main

import (
	"encoding/json"
	"net/http"
)

// GetStoragePoolInfo is the handler for GET /node/{nodeid}/storagepool/{storagepoolname}
// Get detailed information of this storage pool
func (api NodeAPI) GetStoragePoolInfo(w http.ResponseWriter, r *http.Request) {
	var respBody StoragePool
	json.NewEncoder(w).Encode(&respBody)
}
