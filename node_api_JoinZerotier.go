package main

import (
	"encoding/json"
	"net/http"
)

// JoinZerotier is the handler for POST /node/{nodeid}/zerotier
// Join Zerotier network
func (api NodeAPI) JoinZerotier(w http.ResponseWriter, r *http.Request) {
	var reqBody ZerotierJoin

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
