package main

import (
	"encoding/json"
	"net/http"

	client "github.com/g8os/go-client"
	"github.com/gorilla/mux"
	"strconv"
)

// PingContainer is the handler for POST /node/{nodeid}/container/{containerid}/ping
// Ping this container
func (api NodeAPI) PingContainer(w http.ResponseWriter, r *http.Request) {
	var respBody bool
	vars := mux.Vars(r)
	containerID := vars["containerid"]
	cID, err := strconv.Atoi(containerID)
	if err != nil {
		json.NewEncoder(w).Encode(err.Error())
		w.WriteHeader(http.StatusInternalServerError)
		return
	}

	cl := GetConnection(r)
	contMgr := client.Container(cl)
	container := contMgr.Client(cID)
	core := client.Core(container)

	if err := core.Ping(); err != nil {
		respBody = false
	} else {
		respBody = true
	}

	json.NewEncoder(w).Encode(&respBody)
}
