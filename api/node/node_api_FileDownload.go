package node

import (
	"net/http"

	"fmt"

	log "github.com/Sirupsen/logrus"

	"github.com/zero-os/0-core/client/go-client"
	"github.com/zero-os/0-orchestrator/api/tools"
	"github.com/gorilla/mux"
)

// FileDownload is the handler for GET /nodes/{nodeid}/container/{containername}/filesystem
// Download file from container
func (api NodeAPI) FileDownload(w http.ResponseWriter, r *http.Request) {
	path := r.URL.Query().Get("path")
	if path == "" {
		tools.WriteError(w, http.StatusBadRequest, fmt.Errorf("missing path"))
		return
	}

	container, err := tools.GetContainerConnection(r, api)
	if err != nil {
		vars := mux.Vars(r)
		log.Errorf("Failed to connect to container %v: %v", vars["containername"], err.Error())
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	fs := client.Filesystem(container)

	w.Header().Set("Content-Type", "application/octet-stream")
	if err := fs.Download(path, w); err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}
	w.WriteHeader(http.StatusOK)
}
