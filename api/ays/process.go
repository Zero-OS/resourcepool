package ays

import (
	"fmt"
	"strconv"
	"syscall"
	"time"

	goclient "github.com/zero-os/0-core/client/go-client"
)

var errBadProcessID = fmt.Errorf("Processid should be valid positive integer")

// KillProcess kills a process on a node pointed by nodeClient
func (c *Client) KillProcess(pid string, nodeClient goclient.Client) error {
	pID, err := strconv.ParseUint(pid, 10, 64)
	if err != nil {
		return errBadProcessID
	}

	processID := goclient.ProcessId(pID)
	core := goclient.Core(nodeClient)
	signal := syscall.SIGTERM

	for i := 0; i < 4; i++ {
		if i == 3 {
			signal = syscall.SIGKILL
		}

		if err := core.KillProcess(processID, signal); err != nil {
			return fmt.Errorf("Error killing process: %v", err)
		}
		time.Sleep(time.Millisecond * 50)

		if alive, err := core.ProcessAlive(processID); err != nil {
			return fmt.Errorf("Error checking if process alive: %v", err)
		} else if !alive {
			return nil
		}
	}

	return fmt.Errorf("Failed to kill process %v", pID)
}
