package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/gorilla/mux"

	"github.com/zero-os/0-orchestrator/api/tools"
)

// CreateGW is the handler for POST /nodes/{nodeid}/gws
// Create a new gateway
func (api *NodeAPI) MigrateGW(w http.ResponseWriter, r *http.Request) {
	aysClient, err := tools.GetAysConnection(api)
	if err != nil {
		tools.WriteError(w, http.StatusUnauthorized, err, "")
		return
	}

	var reqBody MigrateGW

	vars := mux.Vars(r)
	gwname := vars["gwname"]

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err, "Error decoding request body")
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	exists, err := aysClient.ServiceExists("gateway", gwname, api.AysRepo)
	if err != nil {
		errmsg := fmt.Sprintf("error getting gateway service by name %s ", gwname)
		tools.WriteError(w, http.StatusInternalServerError, err, errmsg)
		return
	}
	if !exists {
		tools.WriteError(w, http.StatusNotFound, fmt.Errorf("gateway with name %s does not exist", gwname), "")
		return
	}

	exists, err = aysClient.ServiceExists("node", reqBody.Node, api.AysRepo)
	if err != nil {
		errmsg := fmt.Sprintf("error getting node service by name %s ", reqBody.Node)
		tools.WriteError(w, http.StatusInternalServerError, err, errmsg)
		return
	}
	if !exists {
		tools.WriteError(w, http.StatusNotFound, fmt.Errorf("node with name %s does not exist", reqBody.Node), "")
		return
	}

	bp := map[string]interface{}{
		fmt.Sprintf("gateway__%s", gwname): map[string]string{
			"node": reqBody.Node,
		},
	}

	_, err = aysClient.UpdateBlueprint(api.AysRepo, "gateway", gwname, "update", bp)

	errmsg := fmt.Sprintf("error executing blueprint for gateway %s creation ", gwname)
	if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
		return
	}

	w.Header().Set("Location", fmt.Sprintf("/nodes/%s/gws/%s", reqBody.Node, gwname))
	w.WriteHeader(http.StatusOK)

}
