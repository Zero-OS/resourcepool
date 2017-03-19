package main

import (
	"encoding/json"
	"fmt"
	"github.com/g8os/go-client"
	"github.com/gorilla/mux"
	"net/http"
	"path"
	"strings"
)

func WriteError(w http.ResponseWriter, code int, err error) {
	w.WriteHeader(code)
	json.NewEncoder(w).Encode(err.Error())

	return
}

func Url(r *http.Request, p ...string) string {
	vars := mux.Vars(r)

	tail := path.Join(p...)
	return strings.TrimRight(fmt.Sprintf("/core0/%s/%s", vars["id"], tail), "/")
}

func ResultUrl(r *http.Request, job client.Job) string {
	return Url(r, "command", string(job))
}
