package main

import (
	"encoding/json"
	"net/http"
)

// MigrateVM is the handler for POST /node/{nodeid}/vm/{vmid}/migrate
// Migrate the VM to another host
func (api NodeAPI) MigrateVM(w http.ResponseWriter, r *http.Request) {
	var reqBody VMMigrate

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
