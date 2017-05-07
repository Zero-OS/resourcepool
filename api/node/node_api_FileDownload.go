package node

import (
	"net/http"

	"fmt"

	"github.com/g8os/go-client"
	"github.com/g8os/resourcepool/api/tools"
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
		tools.WriteError(w, http.StatusInternalServerError, err)
	}

	fs := client.Filesystem(container)

	w.Header().Set("Content-Type", "application/octet-stream")
	w.WriteHeader(http.StatusOK)
	if err := fs.Download(path, w); err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
	}
}
