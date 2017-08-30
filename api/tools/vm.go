package tools

import (
	"fmt"
	"net/http"

	"github.com/gorilla/mux"
)

// ExecuteVMAction executes an action on a vm
func ExecuteVMAction(aystool AYStool, w http.ResponseWriter, r *http.Request, repoName, action string) {
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

	res, err := aystool.ExecuteBlueprint(repoName, "vm", vmID, "action", obj)
	errmsg := fmt.Sprintf("error executing blueprint for vm %s %s", vmID, action)
	if err != nil {
		WriteError(w, http.StatusInternalServerError, err, errmsg)
		return
	}

	if _, err := aystool.WaitRunDone(res.Key, repoName); err != nil {
		httpErr, ok := err.(HTTPError)
		if ok {
			WriteError(w, httpErr.Resp.StatusCode, httpErr, "")
		} else {
			WriteError(w, http.StatusInternalServerError, err, errmsg)
		}
		return
	}
	w.WriteHeader(http.StatusNoContent)
}
