package node

import (
	"encoding/json"
	"net/http"

	client "github.com/g8os/go-client"
	"github.com/g8os/resourcepool/api/tools"
)

// FileDelete is the handler for DELETE /nodes/{nodeid}/container/{containername}/filesystem
// Delete file from container
func (api NodeAPI) FileDelete(w http.ResponseWriter, r *http.Request) {
	var reqBody DeleteFile

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		w.WriteHeader(400)
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		w.WriteHeader(400)
		w.Write([]byte(`{"error":"` + err.Error() + `"}`))
		return
	}

	container, err := tools.GetContainerConnection(r, api)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
	}

	fs := client.Filesystem(container)
	if err := fs.Remove(reqBody.Path); err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
	}

	w.WriteHeader(http.StatusNoContent)
}
