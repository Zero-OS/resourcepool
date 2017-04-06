package node

import (
	"encoding/json"
	"net/http"
)

// SendSignalJob is the handler for POST /node/{nodeid}/container/{containerid}/job
// Send signal to the job
func (api NodeAPI) SendSignalJob(w http.ResponseWriter, r *http.Request) {
	var reqBody ProcessSignal

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
