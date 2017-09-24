package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/gorilla/mux"

	"github.com/zero-os/0-orchestrator/api/tools"
)

// CreateStoragePoolDevices is the handler for POST /nodes/{nodeid}/storagepools/{storagepoolname}/device
// Add extra devices to this storage pool
func (api *NodeAPI) CreateStoragePoolDevices(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)
	vars := mux.Vars(r)
	node := vars["nodeid"]
	storagepool := vars["storagepoolname"]

	devices, notok := api.getStoragePoolDevices(node, storagepool, w, r)
	if notok {
		return
	}

	nodeDevices, errMsg := api.GetNodeDevices(w, r)
	if errMsg != nil {
		tools.WriteError(w, http.StatusInternalServerError, errMsg, "Failed to get Node device")
		return
	}

	deviceMap := map[string]struct{}{}
	for _, dev := range devices {
		deviceMap[dev.Device] = struct{}{}
	}

	// decode request
	var newDevices []string
	defer r.Body.Close()
	if err := json.NewDecoder(r.Body).Decode(&newDevices); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err, "Error decoding request for storagepool creation")
		return
	}

	// add new device to existing ones
	for _, dev := range newDevices {
		if _, exists := deviceMap[dev]; exists {
			continue
		}

		_, ok := nodeDevices[dev]
		if !ok {
			err := fmt.Errorf("Device %v doesn't exist", dev)
			tools.WriteError(w, http.StatusBadRequest, err, "")
			return
		}

		devices = append(devices, DeviceInfo{
			Device: dev,
		})
	}

	bpContent := struct {
		Devices []DeviceInfo `yaml:"devices" json:"devices"`
	}{
		Devices: devices,
	}
	blueprint := map[string]interface{}{
		fmt.Sprintf("storagepool__%s", storagepool): bpContent,
	}

	run, err := aysClient.ExecuteBlueprint(api.AysRepo, "storagepool", storagepool, "addDevices", blueprint)
	errmsg := "Error executing blueprint for storagepool device creation "
	if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
		return
	}

	if _, errr := tools.WaitOnRun(api, w, r, run.Key); errr != nil {
		return
	}

	w.WriteHeader(http.StatusCreated)

}
