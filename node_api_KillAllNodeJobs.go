package main

import (
	"encoding/json"
	"github.com/g8os/go-client"
	"net/http"
)

// KillAllNodeJobs is the handler for DELETE /node/{nodeid}/job
// Kills all running jobs
func (api NodeAPI) KillAllNodeJobs(w http.ResponseWriter, r *http.Request) {
	cl := GetConnection(r)
	core := client.Core(cl)
	err := core.KillAll()
	if err != nil {
		json.NewEncoder(w).Encode(err.Error())
		w.WriteHeader(http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusNoContent)

}
