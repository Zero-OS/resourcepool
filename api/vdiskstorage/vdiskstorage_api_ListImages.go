package vdiskstorage

import (
	"encoding/json"
	"net/http"
)

// ListImages is the handler for GET /vdiskstorage/{vdiskstorageid}/images
// List all vdisk images installed in this VdiskStroage
func (api VdiskstorageAPI) ListImages(w http.ResponseWriter, r *http.Request) {
	var respBody []Image
	json.NewEncoder(w).Encode(&respBody)
}
