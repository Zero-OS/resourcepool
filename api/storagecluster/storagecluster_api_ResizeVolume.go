package storagecluster

import (
	"encoding/json"
	"net/http"
)

// ResizeVolume is the handler for POST /storagecluster/{label}/volumes/{volumeid}/resize
// Resize Volume
func (api StorageclusterAPI) ResizeVolume(w http.ResponseWriter, r *http.Request) {
	var reqBody VolumeResize

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
