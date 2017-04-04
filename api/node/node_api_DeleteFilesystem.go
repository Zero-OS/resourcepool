package node

import (
	"net/http"
)

// DeleteFilesystem is the handler for DELETE /node/{nodeid}/storagepool/{storagepoolname}/filesystem/{filesystemname}
// Delete filesystem
func (api NodeAPI) DeleteFilesystem(w http.ResponseWriter, r *http.Request) {
}
