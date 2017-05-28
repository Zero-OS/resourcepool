package node

import (
	"net/http"

	"bytes"
	"fmt"

	client "github.com/g8os/go-client"
	"github.com/g8os/resourcepool/api/tools"
	"github.com/gorilla/mux"
)

// GetGWHTTPConfig is the handler for GET /nodes/{nodeid}/gws/{gwname}/advanced/http
// Get current HTTP config
// Once used you can not use gw.httpproxxies any longer
func (api NodeAPI) GetGWHTTPConfig(w http.ResponseWriter, r *http.Request) {
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
	err = client.Filesystem(containerClient).Download("/etc/caddy.conf", &config)
	if err != nil {
		fmt.Errorf("Error getting  file from container '%s' at path '%s': %+v.\n", gwname, "/etc/caddy.conf", err)
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	w.Header().Set("Content-Type", "text/plain")
	w.WriteHeader(http.StatusOK)
	w.Write(config.Bytes())
}
