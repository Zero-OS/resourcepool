package node

import (
	"fmt"
	"net/http"

	log "github.com/Sirupsen/logrus"
	"github.com/g8os/resourcepool/api/tools"
	"github.com/gorilla/mux"
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

	// remove device from list of current devices
	updatedDevices := []DeviceInfo{}
	for _, device := range devices {
		if device.PartUUID != toDeleteUUID {
			updatedDevices = append(updatedDevices, DeviceInfo{Device: device.Device})
		}
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
