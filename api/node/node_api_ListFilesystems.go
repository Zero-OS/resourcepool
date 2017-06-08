package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// ListFilesystems is the handler for GET /nodes/{nodeid}/storagepools/{storagepoolname}/filesystem
// List filesystems
func (api NodeAPI) ListFilesystems(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	storagepool := vars["storagepoolname"]

	// only show the filesystem under the storagepool specified in the URL
	querParams := map[string]interface{}{
		"parent": fmt.Sprintf("storagepool!%s", storagepool),
	}

	services, _, err := api.AysAPI.Ays.ListServicesByRole("filesystem", api.AysRepo, nil, querParams)
	if err != nil {
		errmsg := "Error listing storagepool services"
		tools.WriteError(w, http.StatusInternalServerError, err, errmsg)
		return
	}

	respBody := make([]string, len(services), len(services))
	for i, service := range services {
		respBody[i] = service.Name
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
