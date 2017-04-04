package main

import (
	"log"
	"net/http"

	"github.com/g8os/grid/api/goraml"
	"github.com/g8os/grid/api/node"
	"github.com/g8os/grid/api/storagecluster"
	"github.com/g8os/grid/api/tools"

	"fmt"

	"flag"

	"github.com/gorilla/mux"
	"gopkg.in/validator.v2"
)

const (
	port = 5000
)

// AysRepo refers to the ays repository name
var AysRepo string

func main() {
	validator.SetValidationFunc("multipleOf", goraml.MultipleOf)
	AysRepo = *flag.String("repo", "grid", "Name of the repo to use")
	flag.Parse()
	// input validator
	r := mux.NewRouter()

	// home page
	r.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		http.ServeFile(w, r, "index.html")
	})

	// apidocs
	r.PathPrefix("/apidocs/").Handler(http.StripPrefix("/apidocs/", http.FileServer(http.Dir("./apidocs/"))))

	node.NodeInterfaceRoutes(r, node.NewNodeAPI(AysRepo))

	storagecluster.StorageclusterInterfaceRoutes(r, storagecluster.StorageclusterAPI{})

	log.Println("starting server")
	log.Println("Server is listening on port", port)
	err := http.ListenAndServe(fmt.Sprintf(":%d", port), tools.ConnectionMiddleware()(r))
	if err != nil {
		log.Println(err)
	}
}
