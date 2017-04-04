package node

import (
	"net/http"
)

// RebootNode is the handler for POST /node/{nodeid}/reboot
// Immediately reboot the machine.
func (api NodeAPI) RebootNode(w http.ResponseWriter, r *http.Request) {
}
