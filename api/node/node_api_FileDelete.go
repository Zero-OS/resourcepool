package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	client "github.com/zero-os/0-core/client/go-client"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// FileDelete is the handler for DELETE /nodes/{nodeid}/container/{containername}/filesystem
// Delete file from container
func (api NodeAPI) FileDelete(w http.ResponseWriter, r *http.Request) {
	var reqBody DeleteFile

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err)
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err)
		return
	}

	container, err := tools.GetContainerConnection(r, api)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
	}

	fs := client.Filesystem(container)
	res, err := fs.Exists(reqBody.Path)

	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}
	if res != true {
		err := fmt.Errorf("path %s does not exist", reqBody.Path)
		tools.WriteError(w, http.StatusNotFound, err)
		return
	}

	if err := fs.Remove(reqBody.Path); err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
