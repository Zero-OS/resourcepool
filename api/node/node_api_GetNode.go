package node

import (
	"encoding/json"
	"net/http"

	"github.com/g8os/grid/api/tools"
	"github.com/gorilla/mux"
)

// GetNode is the handler for GET /nodes/{nodeid}
// Get detailed information of a node
func (api NodeAPI) GetNode(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	nodeID := vars["nodeid"]

	service, res, err := api.AysAPI.Ays.GetServiceByName(nodeID, "node", api.AysRepo, nil, nil)

	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	if res.StatusCode != http.StatusOK {
		w.WriteHeader(res.StatusCode)
		return
	}

	var respBody Node
	if err := json.Unmarshal(service.Data, &respBody); err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}
	respBody.Id = service.Name

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
