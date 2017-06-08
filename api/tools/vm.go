package tools

import (
	"fmt"
	"net/http"

	"github.com/gorilla/mux"
)

// ExecuteVMAction executes an action on a vm
func ExecuteVMAction(w http.ResponseWriter, r *http.Request, repoName, action string) {
	vars := mux.Vars(r)
	vmID := vars["vmid"]

	obj := map[string]interface{}{
		"actions": []ActionBlock{{
			Action:  action,
			Actor:   "vm",
			Service: vmID,
			Force:   true,
		}},
	}

	if _, err := ExecuteBlueprint(repoName, "vm", vmID, "action", obj); err != nil {
		Error := fmt.Sprintf("error executing blueprint for vm %s %s", vmID, action)
		WriteError(w, http.StatusInternalServerError, err, Error)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}
