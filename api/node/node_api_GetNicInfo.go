package node

import (
	"encoding/json"
	"net/http"

	"github.com/g8os/go-client"
	"github.com/g8os/resourcepool/api/tools"
)

// GetNicInfo is the handler for GET /nodes/{nodeid}/nic
// Get detailed information about the network interfaces in the node
func (api NodeAPI) GetNicInfo(w http.ResponseWriter, r *http.Request) {
	cl, err := tools.GetConnection(r, api)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	info := client.Info(cl)
	result, err := info.Nic()
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	var respBody []NicInfo
	for _, nic := range result {
		var info NicInfo
		for _, addr := range nic.Addrs {
			info.Addrs = append(info.Addrs, addr.Addr)
		}
		info.Flags = nic.Flags
		info.Hardwareaddr = nic.HardwareAddr
		info.Mtu = nic.MTU
		info.Name = nic.Name
		respBody = append(respBody, info)
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
