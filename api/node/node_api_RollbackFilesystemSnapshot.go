package node

import (
	"net/http"
)

// RollbackFilesystemSnapshot is the handler for POST /node/{nodeid}/storagepool/{storagepoolname}/filesystem/{filesystemname}/snapshot/{snapshotname}/rollback
// Rollback the filesystem to the state at the moment the snapshot was taken
func (api NodeAPI) RollbackFilesystemSnapshot(w http.ResponseWriter, r *http.Request) {
}
