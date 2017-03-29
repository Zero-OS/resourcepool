package main

import (
	"net/http"
)

// DeleteFilesystemSnapshot is the handler for DELETE /node/{nodeid}/storagepool/{storagepoolname}/filesystem/{filesystemname}/snapshot/{snapshotname}
// Delete snapshot
func (api NodeAPI) DeleteFilesystemSnapshot(w http.ResponseWriter, r *http.Request) {
}
