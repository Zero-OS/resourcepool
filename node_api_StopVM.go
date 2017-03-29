package main

import (
	"net/http"
)

// StopVM is the handler for POST /node/{nodeid}/vm/{vmid}/stop
// Stops the VM
func (api NodeAPI) StopVM(w http.ResponseWriter, r *http.Request) {
}
