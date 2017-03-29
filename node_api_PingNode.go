package main

import (
	"encoding/json"
	"github.com/g8os/go-client"
	"net/http"
)

// PingNode is the handler for POST /node/{nodeid}/ping
// Ping this node
func (api NodeAPI) PingNode(w http.ResponseWriter, r *http.Request) {
	var respBody bool
	cl := GetConnection(r)
	core := client.Core(cl)

	if err := core.Ping(); err != nil {
		respBody = false
	} else {
		respBody = true
	}

	json.NewEncoder(w).Encode(&respBody)
}
