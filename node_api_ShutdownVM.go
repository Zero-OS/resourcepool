package main

import (
	"net/http"
)

// ShutdownVM is the handler for POST /node/{nodeid}/vm/{vmid}/shutdown
// Gracefully shutdown the VM
func (api NodeAPI) ShutdownVM(w http.ResponseWriter, r *http.Request) {
}
