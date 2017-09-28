package vdiskstorage

import (
	"encoding/json"
	"net/http"
)

// GetImage is the handler for GET /vdiskstorage/{vdiskstorageid}/images/{imageid}
// Get detail about a vdisk image
func (api VdiskstorageAPI) GetImage(w http.ResponseWriter, r *http.Request) {
	var respBody Image
	json.NewEncoder(w).Encode(&respBody)
}
