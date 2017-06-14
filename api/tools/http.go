package tools

import (
	"encoding/json"
	"fmt"
	"net/http"

	log "github.com/Sirupsen/logrus"
)

func WriteError(w http.ResponseWriter, code int, err error, msg string) {
	tracebackError := err.Error()
	log.Errorf(tracebackError)
	if msg == "" {
		msg = tracebackError
	}
	w.Header().Set("content-type", "application/json")
	w.WriteHeader(code)
	v := struct {
		Error string `json:"error"`
	}{Error: msg}

	json.NewEncoder(w).Encode(v)
}

type HTTPError struct {
	Resp *http.Response
	err  error
}

func NewHTTPError(resp *http.Response, msg string, args ...interface{}) HTTPError {
	log.Debug("create http error")
	return HTTPError{
		Resp: resp,
		err:  fmt.Errorf(msg, args...),
	}
}

func (httpErr HTTPError) Error() string {
	return httpErr.err.Error()
}

func HandleAYSResponse(aysErr error, aysRes *http.Response, w http.ResponseWriter, action string) bool {
	if aysErr != nil {
		errmsg := fmt.Sprintf("AYS threw error while %s.\n", action)
		WriteError(w, http.StatusInternalServerError, aysErr, errmsg)
		return false
	}
	if aysRes.StatusCode != http.StatusOK {
		log.Errorf("AYS returned status %v while %s.\n", aysRes.StatusCode, action)
		w.WriteHeader(aysRes.StatusCode)
		return false
	}
	return true
}
