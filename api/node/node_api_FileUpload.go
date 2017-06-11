package node

import (
	"fmt"
	"net/http"

	"github.com/gorilla/mux"
	client "github.com/zero-os/0-core/client/go-client"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// FileUpload is the handler for POST /node/{nodeid}/container/{containername}/filesystem
// Upload file to container
func (api NodeAPI) FileUpload(w http.ResponseWriter, r *http.Request) {
	path := r.URL.Query().Get("path")
	if path == "" {
		tools.WriteError(w, http.StatusBadRequest, fmt.Errorf("missing path"), "")
		return
	}

	if err := r.ParseMultipartForm(4 * 1024 * 1024); err != nil { //4MiB
		tools.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	defer r.MultipartForm.RemoveAll()

	filesList, ok := r.MultipartForm.File["file"]
	if !ok {
		tools.WriteError(w, http.StatusBadRequest, fmt.Errorf("missing file"), "")
		return
	}

	file := filesList[0]
	fd, err := file.Open()
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "Error opening file on host")
		return
	}
	defer fd.Close()

	container, err := tools.GetContainerConnection(r, api)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "Failed to establish connection to container")
		return
	}

	fs := client.Filesystem(container)

	if err := fs.Upload(fd, path); err != nil {
		vars := mux.Vars(r)
		containerName := vars["containername"]
		errmsg := fmt.Sprintf("Error uploading file to container '%s' at path '%s'.\n", containerName, path)
		tools.WriteError(w, http.StatusInternalServerError, err, errmsg)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}
