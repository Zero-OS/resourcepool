package handlers

import (
	"fmt"
	"net/http"

	"github.com/zero-os/0-orchestrator/api/ays"
	"github.com/zero-os/0-orchestrator/api/httperror"
)

// HandleError examines the err error object and will return a correct error notification to the http response
func HandleError(w http.ResponseWriter, err error) {
	if ayserr, ok := err.(*ays.Error); ok {
		ayserr.Handle(w, http.StatusInternalServerError)
	} else {
		httperror.WriteError(w, http.StatusInternalServerError, err, err.Error())
	}
	return
}

// HandleErrorServiceExists examines the err error object and will return a correct error notification to the http response
func HandleErrorServiceExists(w http.ResponseWriter, err error, role string, name string) {
	if err != nil {
		HandleError(w, err)
	} else {
		err = fmt.Errorf("%s with name %s already exists", role, name)
		httperror.WriteError(w, http.StatusConflict, err, "")
	}
}

// HandleErrorServiceDoesNotExists examines the err error object and will return a correct error notification to the http response
func HandleErrorServiceDoesNotExist(w http.ResponseWriter, err error, role string, name string) {
	if err != nil {
		HandleError(w, err)
	} else {
		err = fmt.Errorf("%s with name %s does not exist", role, name)
		httperror.WriteError(w, http.StatusBadRequest, err, "")
	}
}
