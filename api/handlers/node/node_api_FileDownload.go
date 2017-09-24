package node

import (
	"net/http"

	"fmt"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-core/client/go-client"
	"github.com/zero-os/0-orchestrator/api/httperror"
)

// FileDownload is the handler for GET /nodes/{nodeid}/container/{containername}/filesystem
// Download file from container
func (api *NodeAPI) FileDownload(w http.ResponseWriter, r *http.Request) {
	path := r.URL.Query().Get("path")
	if path == "" {
		httperror.WriteError(w, http.StatusBadRequest, fmt.Errorf("missing path"), "")
		return
	}

	// container, err := tools.GetContainerConnection(r, api)
	container, err := api.client.GetContainerConnection(r)
	if err != nil {
		vars := mux.Vars(r)
		errmsg := fmt.Sprintf("Failed to connect to container %v", vars["containername"])
		httperror.WriteError(w, http.StatusInternalServerError, err, errmsg)
		return
	}

	fs := client.Filesystem(container)

	w.Header().Set("Content-Type", "application/octet-stream")
	if err := fs.Download(path, w); err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Error downloading file from container")
		return
	}
	w.WriteHeader(http.StatusOK)
}
