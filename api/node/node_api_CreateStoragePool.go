package node

import (
	"encoding/json"
	"net/http"
)

// CreateStoragePool is the handler for POST /node/{nodeid}/storagepool
// Create a new storage pool
func (api NodeAPI) CreateStoragePool(w http.ResponseWriter, r *http.Request) {
	var reqBody StoragePoolCreate

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		w.WriteHeader(400)
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		w.WriteHeader(400)
		w.Write([]byte(`{"error":"` + err.Error() + `"}`))
		return
	}
}
