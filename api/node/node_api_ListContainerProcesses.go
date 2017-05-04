package node

import (
	"encoding/json"
	"net/http"

	client "github.com/g8os/go-client"
	"github.com/g8os/grid/api/tools"
)

// ListContainerProcesses is the handler for GET /nodes/{nodeid}/containers/{containername}/process
// Get running processes in this container
func (api NodeAPI) ListContainerProcesses(w http.ResponseWriter, r *http.Request) {
	var respBody []Process

	conn, err := tools.GetContainerConnection(r, api)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	core := client.Core(conn)
	processes, err := core.Processes()
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
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
