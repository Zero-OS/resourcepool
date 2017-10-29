package webhook

import (
	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// DeleteWebhook is the handler for DELETE /webhooks/{webhookname}
// Delete a webhook
func (api *WebhooksAPI) DeleteWebhook(w http.ResponseWriter, r *http.Request) {
	aysClient, err := tools.GetAysConnection(api)
	if err != nil {
		tools.WriteError(w, http.StatusUnauthorized, err, "")
		return
	}

	vars := mux.Vars(r)
	webhookName := vars["webhookname"]
	res, err := aysClient.Ays.DeleteServiceByName(webhookName, "webhook", api.AysRepo, nil, nil)
	if !tools.HandleAYSDeleteResponse(err, res, w, "deleting webhook service") {
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
