package node

import (
	"encoding/json"

	"net/http"

	"github.com/gorilla/mux"

	"github.com/zero-os/0-orchestrator/api/handlers"
	"github.com/zero-os/0-orchestrator/api/httperror"
)

// GetFilesystemSnapshotInfo is the handler for GET /nodes/{nodeid}/storagepools/{storagepoolname}/filesystem/{filesystemname}/snapshot/{snapshotname}
// Get detailed information on the snapshot
func (api *NodeAPI) GetFilesystemSnapshotInfo(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)
	snapshotname := mux.Vars(r)["snapshotname"]

	// service, resp, err := aysClient.Ays.GetServiceByName(snapshotname, "fssnapshot", api.AysRepo, nil, nil)
	// if !tools.HandleAYSResponse(err, resp, w, fmt.Sprintf("getting snapshot %s details", snapshotname)) {
	// 	return
	// }
	service, err := api.client.GetService("fssnapshot", snapshotname, "", nil)
	if err != nil {
		handlers.HandleError(w, err)
		return
	}

	var respBody Snapshot

	respBody.Name = snapshotname
	if err := json.Unmarshal(service.Data, &respBody); err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Error unmarshaling ays response")
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(&respBody)
}
