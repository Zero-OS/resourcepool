package node

import (
	"bytes"
	"fmt"
	"net/http"

	client "github.com/g8os/go-client"
	"github.com/g8os/resourcepool/api/tools"
	"github.com/gorilla/mux"
)

// GetGWFWConfig is the handler for GET /nodes/{nodeid}/gws/{gwname}/advanced/firewall
// Get current FW config
// Once used you can not use gw.portforwards any longer
func (api NodeAPI) GetGWFWConfig(w http.ResponseWriter, r *http.Request) {
	var config bytes.Buffer

	vars := mux.Vars(r)
	gwname := vars["gwname"]

	node, err := tools.GetConnection(r, api)
	containerID, err := tools.GetContainerId(r, api, node, gwname)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	containerClient := client.Container(node).Client(containerID)
	err = client.Filesystem(containerClient).Download("/etc/nftables.conf", &config)
	if err != nil {
		fmt.Errorf("Error getting  file from container '%s' at path '%s': %+v.\n", gwname, "/etc/nftables.conf", err)
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	w.Header().Set("Content-Type", "text/plain")
	w.WriteHeader(http.StatusOK)
	w.Write(config.Bytes())
}
