package node

import (
	"encoding/json"
	"net/http"
)

// StartContainerProcess is the handler for POST /node/{nodeid}/container/{containerid}/process
// Start a new process in this container
func (api NodeAPI) StartContainerProcess(w http.ResponseWriter, r *http.Request) {
	var reqBody CoreSystem

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
