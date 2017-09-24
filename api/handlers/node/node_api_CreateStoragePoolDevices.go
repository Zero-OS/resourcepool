package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/gorilla/mux"

	"github.com/zero-os/0-orchestrator/api/ays"
	"github.com/zero-os/0-orchestrator/api/handlers"
	"github.com/zero-os/0-orchestrator/api/httperror"
)

// CreateStoragePoolDevices is the handler for POST /nodes/{nodeid}/storagepools/{storagepoolname}/device
// Add extra devices to this storage pool
func (api *NodeAPI) CreateStoragePoolDevices(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)
	vars := mux.Vars(r)
	node := vars["nodeid"]
	storagepool := vars["storagepoolname"]

	devices, err := api.getStoragePoolDevices(node, storagepool)
	if err != nil {
		handlers.HandleError(w, err)
		return
	}

	nodeDevices, errMsg := api.getNodeDevices(w, r)
	if errMsg != nil {
		httperror.WriteError(w, http.StatusInternalServerError, errMsg, "Failed to get Node device")
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
		httperror.WriteError(w, http.StatusBadRequest, err, "Error decoding request for storagepool creation")
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
			httperror.WriteError(w, http.StatusBadRequest, err, "")
			return
		}

		devices = append(devices, DeviceInfo{
			Device: dev,
		})
	}

	// bpContent := struct {
	// 	Devices []DeviceInfo `yaml:"devices" json:"devices"`
	// }{
	// 	Devices: devices,
	// }
	// blueprint := map[string]interface{}{
	// 	fmt.Sprintf("storagepool__%s", storagepool): bpContent,
	// }

	// run, err := aysClient.ExecuteBlueprint(api.AysRepo, "storagepool", storagepool, "addDevices", blueprint)
	// errmsg := "Error executing blueprint for storagepool device creation "
	// if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
	// 	return
	// }

	// if _, errr := aysClient.WaitOnRun(w, api.AysRepo, run.Key); errr != nil {
	// 	return
	// }

	storagePoolDevices := struct {
		Devices []DeviceInfo `yaml:"devices" json:"devices"`
	}{
		Devices: devices,
	}
	serviceName := fmt.Sprintf("storagepool__%s", storagepool)
	blueprint := ays.Blueprint{
		serviceName: storagePoolDevices,
	}
	blueprintName := ays.BlueprintName("storagepool", storagepool, "addDevices")
	if _, err := api.client.CreateExecRun(blueprintName, blueprint, true); err != nil {
		handlers.HandleError(w, err)
		return
	}

	w.WriteHeader(http.StatusCreated)
}
