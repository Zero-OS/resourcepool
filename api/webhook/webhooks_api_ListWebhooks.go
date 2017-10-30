package webhook

import (
	"encoding/json"
	"net/http"

	"github.com/zero-os/0-orchestrator/api/tools"
)

// ListWebhooks is the handler for GET /webhooks
// List all webhooks
func (api *WebhooksAPI) ListWebhooks(w http.ResponseWriter, r *http.Request) {
	aysClient, err := tools.GetAysConnection(api)
	if err != nil {
		tools.WriteError(w, http.StatusUnauthorized, err, "")
		return
	}

	services, res, err := aysClient.Ays.ListServicesByRole("webhook", api.AysRepo, nil, nil)
	if !tools.HandleAYSResponse(err, res, w, "listing webhooks") {
		return
	}

	var respBody = make([]string, len(services))
	for i, service := range services {
		respBody[i] = service.Name
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
