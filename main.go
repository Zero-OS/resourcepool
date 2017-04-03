package main

import (
	"log"
	"net/http"

	"github.com/g8os/grid/goraml"

	"fmt"

	"github.com/gorilla/mux"
	"gopkg.in/validator.v2"
)

const (
	port = 5000
)

func main() {
	// input validator
	validator.SetValidationFunc("multipleOf", goraml.MultipleOf)

	r := mux.NewRouter()

	// home page
	r.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		http.ServeFile(w, r, "index.html")
	})

	// apidocs
	r.PathPrefix("/apidocs/").Handler(http.StripPrefix("/apidocs/", http.FileServer(http.Dir("./apidocs/"))))

	NodeInterfaceRoutes(r, NodeAPI{})

	StorageclusterInterfaceRoutes(r, StorageclusterAPI{})

	log.Println("starting server")
	log.Println("Server is listening on port", port)
	err := http.ListenAndServe(fmt.Sprintf(":%d", port), ConnectionMiddleware()(r))
	if err != nil {
		log.Println(err)
	}
}
