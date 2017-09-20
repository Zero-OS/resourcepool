package node

import (
	"encoding/json"

	"net/http"

	"fmt"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// GetNode is the handler for GET /nodes/{nodeid}
// Get detailed information of a node
func (api *NodeAPI) GetNode(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)
	vars := mux.Vars(r)
	nodeID := vars["nodeid"]

	service, res, err := aysClient.Ays.GetServiceByName(nodeID, "node", api.AysRepo, nil, nil)

	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, fmt.Sprintf("Error getting node service %s", nodeID))
		return
	}

	if res.StatusCode != http.StatusOK {
		w.WriteHeader(res.StatusCode)
		return
	}

	var respBody NodeService
	if err := json.Unmarshal(service.Data, &respBody); err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "Error unmarshaling ays response")
		return
	}
	var node Node
	node.IPAddress = respBody.RedisAddr
	node.Status = respBody.Status
	node.Hostname = respBody.Hostname
	node.Id = service.Name

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&node)
}
