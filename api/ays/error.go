package ays

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"

	log "github.com/Sirupsen/logrus"
)

// Error is the error return by all the API call
type Error struct {
	resp *http.Response
	err  error
}

func newError(resp *http.Response, err error) *Error {
	return &Error{
		resp: resp,
		err:  err,
	}
}

type aysError struct {
	Code    int    `json:"code"`
	Message string `json:"message"`
}

// Error implements the error interface
func (e *Error) Error() string {
	// Tries to extract an error from the http.Response
	// if response doesn't contain an aysErr, use the e.err

	aysErr := &aysError{}
	errBuf := bytes.Buffer{}

	if e.resp != nil {
		defer e.resp.Body.Close()
		if err := json.NewDecoder(e.resp.Body).Decode(&aysErr); err == nil {
			errBuf.WriteString(fmt.Sprintf("AYS Error (code %v) : %v", aysErr.Code, aysErr.Message))
		}
	}
	if errBuf.Len() == 0 && e.err != nil {
		errBuf.WriteString(e.err.Error())
	}

	return errBuf.String()
}

// Handle is a helper method that will extract all the error message from the error
// and write the proper Status to w
func (e *Error) Handle(w http.ResponseWriter, code int) error {
	tracebackError := e.Error()
	log.Errorf(tracebackError)

	w.Header().Set("content-type", "application/json")
	if e.resp != nil {
		w.WriteHeader(e.resp.StatusCode)
	} else {
		w.WriteHeader(code)
	}

	v := struct {
		Error string `json:"error"`
	}{Error: e.Error()}

	err := json.NewEncoder(w).Encode(v)
	if err != nil {
		log.Errorf("error encoding json error: %v", err)
	}
	return err
}
