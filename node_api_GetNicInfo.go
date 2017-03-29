package main

import (
	"encoding/json"
	"github.com/g8os/go-client"
	"net/http"
)

// GetNicInfo is the handler for GET /node/{nodeid}/nic
// Get detailed information about the network interfaces in the node
func (api NodeAPI) GetNicInfo(w http.ResponseWriter, r *http.Request) {
	cl := GetConnection(r)
	info := client.Info(cl)
	result, err := info.Nic()
	if err != nil {
		json.NewEncoder(w).Encode(err.Error())
		w.WriteHeader(http.StatusInternalServerError)
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

	w.Header().Set("content-type", "application/json")
	json.NewEncoder(w).Encode(&respBody)
}
