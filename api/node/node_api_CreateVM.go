package node

import (
	"encoding/json"
	"net/http"
)

// CreateVM is the handler for POST /node/{nodeid}/vm
// Creates the VM
func (api NodeAPI) CreateVM(w http.ResponseWriter, r *http.Request) {
	var reqBody VMCreate

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
	var respBody int
	json.NewEncoder(w).Encode(&respBody)
}
