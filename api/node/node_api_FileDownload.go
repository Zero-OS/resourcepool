package node

import (
	"net/http"

	"fmt"

	"github.com/g8os/go-client"
	"github.com/g8os/grid/api/tools"
)

// FileDownload is the handler for GET /node/{nodeid}/container/{containerid}/filesystem
// Download file from container
func (api NodeAPI) FileDownload(w http.ResponseWriter, r *http.Request) {
	path := r.URL.Query().Get("path")
	if path == "" {
		tools.WriteError(w, http.StatusBadRequest, fmt.Errorf("missing path"))
		return
	}

	container, err := tools.GetContainerConnection(r)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
	}

	fs := client.Filesystem(container)

	w.Header().Set("content-type", "application/octet-stream")
	if err := fs.Download(path, w); err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
	}
}
