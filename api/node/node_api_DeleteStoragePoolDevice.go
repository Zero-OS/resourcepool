package node

import (
	"fmt"
	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// DeleteStoragePoolDevice is the handler for DELETE /nodes/{nodeid}/storagepools/{storagepoolname}/device/{deviceuuid}
// Removes the device from the storagepool
func (api *NodeAPI) DeleteStoragePoolDevice(w http.ResponseWriter, r *http.Request) {
	aysClient, err := tools.GetAysConnection(api)
	if err != nil {
		tools.WriteError(w, http.StatusUnauthorized, err, "")
		return
	}
	vars := mux.Vars(r)
	node := vars["nodeid"]
	storagePool := vars["storagepoolname"]
	toDeleteUUID := vars["deviceuuid"]

	devices, errBool := api.getStoragePoolDevices(node, storagePool, w, r)
	if errBool {
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
		w.WriteHeader(http.StatusNoContent)
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

	_, err = aysClient.ExecuteBlueprint(api.AysRepo, "storagepool", storagePool, "removeDevices", blueprint)
	errmsg := "Error executing blueprint for storagepool device deletion "
	if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
