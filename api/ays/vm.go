package ays

import (
	"net/http"

	"github.com/gorilla/mux"
)

// ExecuteVMAction is a helper method that send a blueprint with an action block
// to execute an action on a vm
// the VM id is extracted from r
func (c *Client) ExecuteVMAction(r *http.Request, action string) error {
	vars := mux.Vars(r)
	vmID := vars["vmid"]

	bp := Blueprint{
		"actions": []ActionBlock{{
			Action:  action,
			Actor:   "vm",
			Service: vmID,
			Force:   true,
		}},
	}

	bpName := BlueprintName("vm", vmID, "action")
	_, err := c.CreateExecRun(bpName, bp, true)
	return err
}
