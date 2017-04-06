package tools

import (
	"encoding/json"
	"fmt"
	"net/http"

	log "github.com/Sirupsen/logrus"
)

func WriteError(w http.ResponseWriter, code int, err error) {
	w.Header().Set("content-type", "application/json")
	w.WriteHeader(code)
	v := struct {
		Error string `json:"error"`
	}{Error: err.Error()}

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
