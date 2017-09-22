package node

import (
	"encoding/json"
	"fmt"

	"github.com/zero-os/0-orchestrator/api/ays"

	"net/http"

	"reflect"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/handlers"
	"github.com/zero-os/0-orchestrator/api/httperror"
)

// UpdateGateway is the handler for PUT /nodes/{nodeid}/gws/{gwname}
// Update Gateway
func (api *NodeAPI) UpdateGateway(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)
	var reqBody GW
	vars := mux.Vars(r)
	gwID := vars["gwname"]

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		httperror.WriteError(w, http.StatusBadRequest, err, "Error decoding request body")
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		httperror.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	service, err := api.client.GetService("gateway", gwID, "", nil)
	if err != nil {
		handlers.HandleError(w, err)
		return
	}
	// service, res, err := aysClient.Ays.GetServiceByName(gwID, "gateway", api.AysRepo, nil, nil)
	// if !tools.HandleAYSResponse(err, res, w, "Getting storagepool service") {
	// 	return
	// }

	var data CreateGWBP
	if err := json.Unmarshal(service.Data, &data); err != nil {
		errMessage := fmt.Sprintf("Error Unmarshal gateway service '%s'", gwID)
		httperror.WriteError(w, http.StatusInternalServerError, err, errMessage)
		return
	}

	if data.Advanced {
		if !reflect.DeepEqual(data.Httpproxies, reqBody.Httpproxies) {
			errMessage := fmt.Errorf("Advanced options enabled: cannot adjust httpproxies for gateway")
			httperror.WriteError(w, http.StatusForbidden, errMessage, "")
			return
		}
	}

	obj := ays.Blueprint{
		fmt.Sprintf("gateway__%s", gwID): reqBody,
	}

	bpName := ays.BlueprintName("gateway", gwID, "update")
	if err := api.client.CreateExec(bpName, bp); err != nil {
		handlers.HandleError(w, err)
		return
	}
	// _, err = aysClient.ExecuteBlueprint(api.AysRepo, "gateway", gwID, "update", obj)

	// errmsg := fmt.Sprintf("error executing blueprint for gateway %s creation ", gwID)
	// if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
	// 	return
	// }

	w.WriteHeader(http.StatusNoContent)
}
