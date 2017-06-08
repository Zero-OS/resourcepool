package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-core/client/go-client"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// CreateStoragePool is the handler for POST /nodes/{nodeid}/storagepools
// Create a new storage pool
func (api NodeAPI) CreateStoragePool(w http.ResponseWriter, r *http.Request) {
	var reqBody StoragePoolCreate
	node := mux.Vars(r)["nodeid"]

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		errmsg := "Error decoding request for storagepool creation"
		tools.WriteError(w, http.StatusBadRequest, err, errmsg)
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		errmsg := "Error validating request for storagepool creation "
		tools.WriteError(w, http.StatusBadRequest, err, errmsg)
		return
	}

	devices, err := api.GetNodeDevices(w, r)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "Failed to get Node device")
		return
	}

	type partitionMap struct {
		Device   string `yaml:"device" json:"device"`
		PartUUID string `yaml:"partUUID" json:"partUUID"`
	}

	bpContent := struct {
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
			tools.WriteError(w, http.StatusBadRequest, err, "")
			return
		}
		bpContent.Devices = append(bpContent.Devices, partitionMap{Device: device})
	}

	blueprint := map[string]interface{}{
		fmt.Sprintf("storagepool__%s", reqBody.Name): bpContent,
		"actions": []tools.ActionBlock{{
			Action:  "install",
			Actor:   "storagepool",
			Service: reqBody.Name}},
	}

	if _, err := tools.ExecuteBlueprint(api.AysRepo, "storagepool", reqBody.Name, "install", blueprint); err != nil {
		httpErr := err.(tools.HTTPError)
		errmsg := "Error executing blueprint for storagepool creation "
		tools.WriteError(w, httpErr.Resp.StatusCode, httpErr, errmsg)
		return
	}

	w.Header().Set("Location", fmt.Sprintf("/nodes/%s/storagepools/%s", node, reqBody.Name))
	w.WriteHeader(http.StatusCreated)
}

func (api NodeAPI) GetNodeDevices(w http.ResponseWriter, r *http.Request) (map[string]struct{}, error) {
	cl, err := tools.GetConnection(r, api)
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
