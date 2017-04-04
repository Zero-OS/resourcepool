package node

import (
	"encoding/json"
	"net/http"
)

// GetFilesystemInfo is the handler for GET /node/{nodeid}/storagepool/{storagepoolname}/filesystem/{filesystemname}
// Get detailed filesystem information
func (api NodeAPI) GetFilesystemInfo(w http.ResponseWriter, r *http.Request) {
	var respBody Filesystem
	json.NewEncoder(w).Encode(&respBody)
}
