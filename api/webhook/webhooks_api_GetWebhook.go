package webhook

import (
	"encoding/json"
	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// GetWebhook is the handler for GET /webhooks/{webhookname}
// Get a webhook
func (api *WebhooksAPI) GetWebhook(w http.ResponseWriter, r *http.Request) {
	aysClient, err := tools.GetAysConnection(api)
	if err != nil {
		tools.WriteError(w, http.StatusUnauthorized, err, "")
		return
	}

	vars := mux.Vars(r)
	webhookName := vars["webhookname"]
	service, res, err := aysClient.Ays.GetServiceByName(webhookName, "webhook", api.AysRepo, nil, nil)

	if !tools.HandleAYSResponse(err, res, w, "Getting webhook service") {
		return
	}

	var respBody Webhook
	if err := json.Unmarshal(service.Data, &respBody); err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "Error unmrshaling ays response")
		return
	}

	respBody.Name = webhookName

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)

}
