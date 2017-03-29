package main

import (
	"encoding/json"
	"net/http"
)

// CreateContainer is the handler for POST /node/{nodeid}/container
// Create a new Container
func (api NodeAPI) CreateContainer(w http.ResponseWriter, r *http.Request) {
	var reqBody Container

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
