package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	"reflect"

	log "github.com/Sirupsen/logrus"
	"github.com/zero-os/0-orchestrator/api/tools"
	"github.com/gorilla/mux"
)

// UpdateGateway is the handler for PUT /nodes/{nodeid}/gws/{gwname}
// Update Gateway
func (api NodeAPI) UpdateGateway(w http.ResponseWriter, r *http.Request) {
	var reqBody GW
	vars := mux.Vars(r)
	gwID := vars["gwname"]

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err)
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err)
		return
	}

	service, res, err := api.AysAPI.Ays.GetServiceByName(gwID, "gateway", api.AysRepo, nil, nil)
	if !tools.HandleAYSResponse(err, res, w, "Getting storagepool service") {
		return
	}

	var data CreateGWBP
	if err := json.Unmarshal(service.Data, &data); err != nil {
		errMessage := fmt.Errorf("Error Unmarshal gateway service '%s' data: %+v", gwID, err)
		log.Error(errMessage)
		tools.WriteError(w, http.StatusInternalServerError, errMessage)
		return
	}

	if data.Advanced {
		if !reflect.DeepEqual(data.Httpproxies, reqBody.Httpproxies) {
			errMessage := fmt.Errorf("Advanced options enabled: cannot adjust httpproxies for gateway")
			tools.WriteError(w, http.StatusForbidden, errMessage)
			return
		}
	}

	obj := make(map[string]interface{})
	obj[fmt.Sprintf("gateway__%s", gwID)] = reqBody

	if _, err := tools.ExecuteBlueprint(api.AysRepo, "gateway", gwID, "update", obj); err != nil {
		log.Errorf("error executing blueprint for gateway %s creation : %+v", gwID, err)
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
