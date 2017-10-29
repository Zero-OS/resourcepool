package webhook

import (
	"encoding/json"
	"net/http"
	"github.com/zero-os/0-orchestrator/api/tools"
	"github.com/gorilla/mux"
	"fmt"
)

// UpdateWebhook is the handler for PUT /webhooks/{webhookname}
// Update a webhook
func (api *WebhooksAPI) UpdateWebhook(w http.ResponseWriter, r *http.Request) {
	aysClient, err := tools.GetAysConnection(api)
	if err != nil {
		tools.WriteError(w, http.StatusUnauthorized, err, "")
		return
	}
	vars := mux.Vars(r)
	webhookName := vars["webhookname"]
	var reqBody WebhookUpdate

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err, "")
		return
	}


	exists, err := aysClient.ServiceExists("webhook", webhookName, api.AysRepo)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "Error checking webhook service exists")
		return
	} else if !exists {
		w.WriteHeader(http.StatusNotFound)
		return
	}

	bp := struct {
		EventTypes []EnumEventType `json:"eventtypes" validate:"nonzero"`
		Url        string          `json:"url" validate:"nonzero"`
	}{
		Url:        reqBody.Url,
		EventTypes: reqBody.EventTypes,
	}

	obj := make(map[string]interface{})
	obj[fmt.Sprintf("webhook__%s", webhookName)] = bp

	_, err = aysClient.ExecuteBlueprint(api.AysRepo, "webhook", webhookName, "update", obj)
	errmsg := fmt.Sprintf("error executing blueprint for webhook %s update", webhookName)
	if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
