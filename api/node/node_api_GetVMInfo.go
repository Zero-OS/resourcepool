package node

import (
	"encoding/json"
	"net/http"

	"github.com/gorilla/mux"
	g8client "github.com/zero-os/0-core/client/go-client"

	"fmt"

	"github.com/zero-os/0-orchestrator/api/tools"
)

// GetVMInfo is the handler for GET /nodes/{nodeid}/vms/{vmid}/info
// Get statistical information about the virtual machine.
func (api *NodeAPI) GetVMInfo(w http.ResponseWriter, r *http.Request) {
	var respBody VMInfo

	vars := mux.Vars(r)
	vmid := vars["vmid"]

	cl, err := tools.GetConnection(r, api)
	if err != nil {
		errmsg := fmt.Sprintf("Error: in getting VM %s information", vmid)
		tools.WriteError(w, http.StatusInternalServerError, err, errmsg)
		return
	}

	kvmManager := g8client.Kvm(cl)
	vms, err := kvmManager.List()
	if err != nil {
		errmsg := fmt.Sprintf("Error: in getting VM %s information", vmid)
		tools.WriteError(w, http.StatusInternalServerError, err, errmsg)
		return
	}

	var uuid string
	for _, vm := range vms {
		if vm.Name == vmid {
			uuid = vm.UUID
		}
	}

	if uuid == "" {
		err = fmt.Errorf("VM %s is not found", vmid)
		tools.WriteError(w, http.StatusNotFound, err, "")
		return
	}

	vminfo, err := kvmManager.InfoPs(uuid)
	if err != nil {
		errmsg := fmt.Sprintf("Error: in getting VM %s information", vmid)
		tools.WriteError(w, http.StatusInternalServerError, err, errmsg)
		return
	}

	// Get CPU info
	for _, cpu := range vminfo.Vcpu {
		respBody.CPU = append(respBody.CPU, cpu.Time)
	}

	respBody.Disk = []VMDiskInfo{}
	// Get Disk Information
	for _, disk := range vminfo.Block {
		diskInfo := VMDiskInfo{
			ReadThroughput:  disk.RdBytes,
			ReadIops:        disk.RdTimes,
			WriteThroughput: disk.WrBytes,
			WriteIops:       disk.WrTimes,
		}
		respBody.Disk = append(respBody.Disk, diskInfo)
	}

	respBody.Net = []VMNetInfo{}
	// Get network information
	for _, net := range vminfo.Network {
		netInfo := VMNetInfo{
			ReceivedPackets:       net.RxPkts,
			ReceivedThroughput:    net.RxBytes,
			TransmittedPackets:    net.TxPkts,
			TransmittedThroughput: net.TxBytes,
		}
		respBody.Net = append(respBody.Net, netInfo)
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
