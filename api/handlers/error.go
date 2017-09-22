package handlers

import (
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
