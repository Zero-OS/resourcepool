package node

import (
	"encoding/json"
	"fmt"
	"net/http"
	"time"

	"github.com/g8os/grid/api/tools"
	"github.com/gorilla/mux"

	log "github.com/Sirupsen/logrus"
)

// CreateStoragePool is the handler for POST /node/{nodeid}/storagepool
// Create a new storage pool
func (api NodeAPI) CreateStoragePool(w http.ResponseWriter, r *http.Request) {
	var reqBody StoragePoolCreate
	node := mux.Vars(r)["nodeid"]

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		log.Errorf("Error decoding request for storagepool creation : %+v", err)
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		log.Errorf("Error validating request for storagepool creation : %+v", err)
		tools.WriteError(w, http.StatusBadRequest, err)
		return
	}

	bpContent := struct {
		DataProfile     EnumStoragePoolCreateDataProfile     `json:"dataProfile"`
		Devices         []string                             `json:"devices"`
		MetadataProfile EnumStoragePoolCreateMetadataProfile `json:"metadataProfile"`
		Node            string                               `json:"node"`
	}{
		DataProfile:     reqBody.DataProfile,
		MetadataProfile: reqBody.MetadataProfile,
		Devices:         reqBody.Devices,
		Node:            node,
	}

	blueprint := map[string]interface{}{
		fmt.Sprintf("storagepool__%s", reqBody.Name): bpContent,
		"actions": []map[string]string{{"action": "install"}},
	}

	blueprintName := fmt.Sprintf("storagepool__%s_create_%d", node, time.Now().Unix())
	if _, err := tools.ExecuteBlueprint(api.AysRepo, blueprintName, blueprint); err != nil {
		httpErr := err.(tools.HTTPError)
		log.Errorf("Error executing blueprint for storagepool creation : %+v", err.Error())
		tools.WriteError(w, httpErr.Resp.StatusCode, httpErr)
	}
}
