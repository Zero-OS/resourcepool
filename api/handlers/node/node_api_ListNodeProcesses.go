package node

import (
	"encoding/json"
	"net/http"

	client "github.com/zero-os/0-core/client/go-client"
	"github.com/zero-os/0-orchestrator/api/httperror"
)

// ListNodeProcesses is the handler for GET /nodes/{nodeid}/processes
func (api *NodeAPI) ListNodeProcesses(w http.ResponseWriter, r *http.Request) {
	var respBody []Process

	conn, err := api.client.GetNodeConnection(r)
	if err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Failed to establish connection to node")
		return
	}

	core := client.Core(conn)
	processes, err := core.Processes()
	if err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, err, "Error getting processes from node")
		return
	}

	for _, process := range processes {

		cpu := CPUStats{
			GuestNice: process.Cpu.GuestNice,
			Idle:      process.Cpu.Idle,
			IoWait:    process.Cpu.IoWait,
			Irq:       process.Cpu.Irq,
			Nice:      process.Cpu.Nice,
			SoftIrq:   process.Cpu.SoftIrq,
			Steal:     process.Cpu.Steal,
			Stolen:    process.Cpu.Stolen,
			System:    process.Cpu.System,
			User:      process.Cpu.User,
		}
		pr := Process{
			Cmdline: process.Command,
			Cpu:     cpu,
			Pid:     uint64(process.PID),
			Rss:     process.RSS,
			Swap:    process.Swap,
			Vms:     process.VMS,
		}
		respBody = append(respBody, pr)
	}
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)

}
