package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/zero-os/0-orchestrator/api/ays"
	"github.com/zero-os/0-orchestrator/api/handlers"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-core/client/go-client"

	"github.com/zero-os/0-orchestrator/api/httperror"
)

// CreateStoragePool is the handler for POST /nodes/{nodeid}/storagepools
// Create a new storage pool
func (api *NodeAPI) CreateStoragePool(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)
	var reqBody StoragePoolCreate
	node := mux.Vars(r)["nodeid"]

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		errmsg := "Error decoding request for storagepool creation"
		httperror.WriteError(w, http.StatusBadRequest, err, errmsg)
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		httperror.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	devices, err := api.getNodeDevices(w, r)
	if err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Failed to get Node device")
		return
	}

	type partitionMap struct {
		Device   string `yaml:"device" json:"device"`
		PartUUID string `yaml:"partUUID" json:"partUUID"`
	}

	storagePool := struct {
		DataProfile     EnumStoragePoolCreateDataProfile     `yaml:"dataProfile" json:"dataProfile"`
		Devices         []partitionMap                       `yaml:"devices" json:"devices"`
		MetadataProfile EnumStoragePoolCreateMetadataProfile `yaml:"metadataProfile" json:"metadataProfile"`
		Node            string                               `yaml:"node" json:"node"`
	}{
		DataProfile:     reqBody.DataProfile,
		MetadataProfile: reqBody.MetadataProfile,
		Node:            node,
	}

	for _, device := range reqBody.Devices {
		_, ok := devices[device]
		if !ok {
			err := fmt.Errorf("Device %v doesn't exist", device)
			httperror.WriteError(w, http.StatusBadRequest, err, "")
			return
		}
		storagePool.Devices = append(storagePool.Devices, partitionMap{Device: device})
	}

	serviceName := fmt.Sprintf("storagepool__%s", reqBody.Name)
	blueprint := ays.Blueprint{
		serviceName: storagePool,
		"actions": []ays.ActionBlock{{
			Action:  "install",
			Actor:   "storagepool",
			Service: reqBody.Name}},
	}

	blueprintName := ays.BlueprintName("storagepool", reqBody.Name, "install")
	if _, err := api.client.CreateExecRun(blueprintName, blueprint, true); err != nil {
		handlers.HandleError(w, err)
		return
	}

	// run, err := aysClient.ExecuteBlueprint(api.AysRepo, "storagepool", reqBody.Name, "install", blueprint)
	// errmsg := "Error executing blueprint for storagepool creation "
	// if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
	// 	return
	// }

	// if _, errr := aysClient.WaitOnRun(w, api.AysRepo, run.Key); errr != nil {
	// 	return
	// }
	w.Header().Set("Location", fmt.Sprintf("/nodes/%s/storagepools/%s", node, reqBody.Name))
	w.WriteHeader(http.StatusCreated)
}

func (api *NodeAPI) getNodeDevices(w http.ResponseWriter, r *http.Request) (map[string]struct{}, error) {

	cl, err := api.client.GetNodeConnection(r)
	if err != nil {
		return nil, err
	}

	diskClient := client.Disk(cl)
	disks, err := diskClient.List()
	if err != nil {
		return nil, err
	}

	devices := make(map[string]struct{})
	for _, dev := range disks.BlockDevices {
		devices[fmt.Sprintf("/dev/%v", dev.Kname)] = struct{}{}
	}
	return devices, nil
}
