package main

import (
	"encoding/json"
	"net/http"
)

// ListNodeProcesses is the handler for GET /node/{nodeid}/process
// Get Processes
func (api NodeAPI) ListNodeProcesses(w http.ResponseWriter, r *http.Request) {
	var respBody []Process
	//cl := GetConnection(r)
	//core := client.Core(cl)
	//
	//processes, err := core.Processes()
	//if err != nil {
	//	json.NewEncoder(w).Encode(err.Error())
	//	w.WriteHeader(http.StatusInternalServerError)
	//	return
	//}
	//
	//for _, ps := range processes {
	//	var process Process
	//	process.Cmd.Id = ps.Command.ID
	//	process.Cmd.Queue = ps.Command.Queue
	//	process.Cmd.Tags = ps.Command.Tags
	//	process.Cmd.StatsInterval = ps.Command.StatsInterval
	//	process.Cmd.MaxTime = ps.Command.MaxTime
	//	process.Cmd.MaxRestart = ps.Command.MaxRestart
	//	process.Cmd.RecurringPeriod = ps.Command.RecurringPeriod
	//	process.Cmd.LogLevels = ps.Command.LogLevels
	//
	//	process.Cpu = ps.CPU
	//	process.Rss = ps.RSS
	//	process.Swap = ps.Swap
	//	process.Vms = ps.VMS
	//	process.Name = ps.Command.Command
	//
	//}

	json.NewEncoder(w).Encode(&respBody)

}
