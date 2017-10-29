package webhook

import (
	"encoding/json"
	"fmt"
	"github.com/zero-os/0-orchestrator/api/tools"
	"net/http"
)

// CreateWebhook is the handler for POST /webhooks
// Create Webhook
func (api *WebhooksAPI) CreateWebhook(w http.ResponseWriter, r *http.Request) {
	aysClient, err := tools.GetAysConnection(api)
	if err != nil {
		tools.WriteError(w, http.StatusUnauthorized, err, "")
		return
	}
	var reqBody Webhook

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

	exists, err := aysClient.ServiceExists("webhook", reqBody.Name, api.AysRepo)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "Error checking webhook service exists")
		return
	} else if exists {
		err = fmt.Errorf("Webhook with name %s already exists", reqBody.Name)
		tools.WriteError(w, http.StatusConflict, err, "")
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
	obj[fmt.Sprintf("webhook__%s", reqBody.Name)] = bp

	_, err = aysClient.ExecuteBlueprint(api.AysRepo, "webhook", reqBody.Name, "create", obj)
	errmsg := fmt.Sprintf("error executing blueprint for webhook %s creation", reqBody.Name)
	if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
		return
	}

	w.Header().Set("Location", fmt.Sprintf("/webhook/%s", reqBody.Name))
	w.WriteHeader(http.StatusCreated)

}
