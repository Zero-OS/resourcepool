package tools

import (
	"net/http"

	log "github.com/Sirupsen/logrus"
	"github.com/gorilla/mux"
)

// ExecuteVMAction executes an action on a vm
func ExecuteVMAction(w http.ResponseWriter, r *http.Request, repoName, action string) {
	vars := mux.Vars(r)
	vmID := vars["vmid"]

	obj := map[string]interface{}{
		"actions": []ActionBlock{{
			"action":  action,
			"actor":   "vm",
			"service": vmID,
			"force":   true,
		}},
	}

	if _, err := ExecuteBlueprint(repoName, "vm", vmID, "action", obj); err != nil {
		log.Errorf("error executing blueprint for vm %s %s : %+v", vmID, action, err)
		WriteError(w, http.StatusInternalServerError, err)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}
