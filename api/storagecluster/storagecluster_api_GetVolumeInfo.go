package storagecluster

import (
	"encoding/json"
	"net/http"
)

// GetVolumeInfo is the handler for GET /storagecluster/{label}/volumes/{volumeid}
// Get volume information
func (api StorageclusterAPI) GetVolumeInfo(w http.ResponseWriter, r *http.Request) {
	var respBody Volume
	json.NewEncoder(w).Encode(&respBody)
}
