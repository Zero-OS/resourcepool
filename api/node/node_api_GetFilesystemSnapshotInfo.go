package node

import (
	"encoding/json"
	"net/http"
)

// GetFilesystemSnapshotInfo is the handler for GET /node/{nodeid}/storagepool/{storagepoolname}/filesystem/{filesystemname}/snapshot/{snapshotname}
// Get detailed information on the snapshot
func (api NodeAPI) GetFilesystemSnapshotInfo(w http.ResponseWriter, r *http.Request) {
	var respBody Snapshot
	json.NewEncoder(w).Encode(&respBody)
}
