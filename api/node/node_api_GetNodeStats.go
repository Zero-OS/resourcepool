package node

import (
	"encoding/json"
	"net/http"

	"github.com/zero-os/0-core/client/go-client"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// GetNodeStats is the handler for GET /nodes/{nodeid}/stats
// The aggregated stats of node
func (api NodeAPI) GetNodeStats(w http.ResponseWriter, r *http.Request) {
	cl, err := tools.GetConnection(r, api)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "Failed to establish connection to node")
		return
	}

	aggregator := client.Aggregator(cl)
	stats, err := aggregator.Query()

	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "Error getting statistics of node")
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&stats)
}
