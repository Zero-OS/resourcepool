package tools

import (
	"syscall"
	"net/http"
	"time"
	"fmt"
	"github.com/zero-os/0-core/client/go-client"
	"strconv"
)

func KillProcess(pid string, cl client.Client, w http.ResponseWriter) {
	pID, err := strconv.ParseUint(pid, 10, 64)
	if err != nil {
		WriteError(w, http.StatusInternalServerError, err)
		return
	}

	processID := client.ProcessId(pID)
	core := client.Core(cl)
	signal := syscall.SIGTERM

	for i := 0; i < 4; i++ {
		if i == 3 {
			signal = syscall.SIGKILL
		}

		if err := core.KillProcess(processID, signal); err != nil {
			WriteError(w, http.StatusInternalServerError, err)
			return
		}
		time.Sleep(time.Millisecond * 50)

		if alive, err := core.ProcessAlive(processID); err != nil {
			WriteError(w, http.StatusInternalServerError, err)
			return
		} else if !alive {
			w.WriteHeader(http.StatusNoContent)
			return
		}
	}

	err = fmt.Errorf("Failed to kill process %v", pID)
	WriteError(w, http.StatusInternalServerError, err)
}