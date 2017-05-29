package node

import (
	"encoding/json"
	"net/http"
	"strconv"

	client "github.com/zero-os/go-client"
	"github.com/zero-os/0-rest-api/api/tools"
	"github.com/gorilla/mux"
)

// GetContainerProcess is the handler for GET /nodes/{nodeid}/containers/{containername}/processes/{processid}
// Get process details
func (api NodeAPI) GetContainerProcess(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	conn, err := tools.GetContainerConnection(r, api)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	pId, err := strconv.ParseUint(vars["processid"], 10, 64)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	processID := client.ProcessId(pId)
	core := client.Core(conn)
	process, err := core.Process(processID)

	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

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

	respBody := Process{
		Cmdline: process.Command,
		Cpu:     cpu,
		Pid:     pId,
		Rss:     process.RSS,
		Swap:    process.Swap,
		Vms:     process.VMS,
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
