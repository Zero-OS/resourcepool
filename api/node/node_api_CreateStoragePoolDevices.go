package node

import (
	"encoding/json"
	"fmt"
	"net/http"

	log "github.com/Sirupsen/logrus"
	"github.com/zero-os/0-orchestrator/api/tools"
	"github.com/gorilla/mux"
)

// CreateStoragePoolDevices is the handler for POST /nodes/{nodeid}/storagepools/{storagepoolname}/device
// Add extra devices to this storage pool
func (api NodeAPI) CreateStoragePoolDevices(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	node := vars["nodeid"]
	storagepool := vars["storagepoolname"]

	devices, err := api.getStoragePoolDevices(node, storagepool, w)
	if err {
		return
	}

	nodeDevices, errMsg := api.GetNodeDevices(w, r)
	if errMsg != nil {
		tools.WriteError(w, http.StatusInternalServerError, errMsg)
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
		tools.WriteError(w, http.StatusBadRequest, err)
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
			tools.WriteError(w, http.StatusBadRequest, err)
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

	if _, err := tools.ExecuteBlueprint(api.AysRepo, "storagepool", storagepool, "addDevices", blueprint); err != nil {
		httpErr := err.(tools.HTTPError)
		log.Errorf("Error executing blueprint for storagepool device creation : %+v", err.Error())
		tools.WriteError(w, httpErr.Resp.StatusCode, httpErr)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
