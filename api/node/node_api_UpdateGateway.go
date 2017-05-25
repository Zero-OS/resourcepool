package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/g8os/blockstor/log"
	"github.com/g8os/resourcepool/api/tools"
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

	obj := make(map[string]interface{})
	obj[fmt.Sprintf("gateway__%s", gwID)] = reqBody

	if _, err := tools.ExecuteBlueprint(api.AysRepo, "gateway", gwID, "update", obj); err != nil {
		log.Errorf("error executing blueprint for gateway %s creation : %+v", gwID, err)
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
