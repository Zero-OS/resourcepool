package node

import (
	"net/http"
)

// ExitZerotier is the handler for DELETE /node/{nodeid}/zerotier/{zerotierid}
// Exit the Zerotier network
func (api NodeAPI) ExitZerotier(w http.ResponseWriter, r *http.Request) {
}
