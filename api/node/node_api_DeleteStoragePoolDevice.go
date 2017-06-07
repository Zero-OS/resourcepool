package node

import (
	"fmt"
	"net/http"

	log "github.com/Sirupsen/logrus"
	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// DeleteStoragePoolDevice is the handler for DELETE /nodes/{nodeid}/storagepools/{storagepoolname}/device/{deviceuuid}
// Removes the device from the storagepool
func (api NodeAPI) DeleteStoragePoolDevice(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	node := vars["nodeid"]
	storagePool := vars["storagepoolname"]
	toDeleteUUID := vars["deviceuuid"]

	devices, err := api.getStoragePoolDevices(node, storagePool, w)
	if err {
		return
	}

	var exists bool
	// remove device from list of current devices
	updatedDevices := []DeviceInfo{}
	for _, device := range devices {
		if device.PartUUID != toDeleteUUID {
			updatedDevices = append(updatedDevices, DeviceInfo{Device: device.Device})
		} else {
			exists = true
		}
	}
	if !exists {
		tools.WriteError(w, http.StatusNotFound, fmt.Errorf("Device %v not found", toDeleteUUID))
		return
	}

	bpContent := struct {
		Devices []DeviceInfo `yaml:"devices" json:"devices"`
	}{
		Devices: updatedDevices,
	}
	blueprint := map[string]interface{}{
		fmt.Sprintf("storagepool__%s", storagePool): bpContent,
	}

	if _, err := tools.ExecuteBlueprint(api.AysRepo, "storagepool", storagePool, "removeDevices", blueprint); err != nil {
		httpErr := err.(tools.HTTPError)
		log.Errorf("Error executing blueprint for storagepool device deletion : %+v", err.Error())
		tools.WriteError(w, httpErr.Resp.StatusCode, httpErr)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
