package tools

import (
	"encoding/json"
	"net/http"
)

func WriteError(w http.ResponseWriter, code int, err error) {
	w.Header().Set("content-type", "application/json")
	w.WriteHeader(code)
	v := struct {
		Error string `json:"error"`
	}{Error: err.Error()}

	json.NewEncoder(w).Encode(v)

	return
}
