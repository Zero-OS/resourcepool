package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/gorilla/mux"

	tools "github.com/g8os/grid/api/tools"
)

// GetFilesystemSnapshotInfo is the handler for GET /nodes/{nodeid}/storagepools/{storagepoolname}/filesystem/{filesystemname}/snapshot/{snapshotname}
// Get detailed information on the snapshot
func (api NodeAPI) GetFilesystemSnapshotInfo(w http.ResponseWriter, r *http.Request) {
	snapshotname := mux.Vars(r)["snapshotname"]

	service, resp, err := api.AysAPI.Ays.GetServiceByName(snapshotname, "fssnapshot", api.AysRepo, nil, nil)
	if !tools.HandleAYSResponse(err, resp, w, fmt.Sprintf("getting snapshot %s details", snapshotname)) {
		return
	}

	var respBody Snapshot

	respBody.Name = snapshotname
	if err := json.Unmarshal(service.Data, &respBody); err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(&respBody)
}
