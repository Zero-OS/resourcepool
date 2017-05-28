package node

import (
	"net/http"
)

// AddGWDHCPHost is the handler for POST /nodes/{nodeid}/gws/{gwname}/dhcp/{interface}/hosts
// Add a dhcp host to a specified interface
func (api NodeAPI) AddGWDHCPHost(w http.ResponseWriter, r *http.Request) {
}
