package router

import (
	"net/http"

	log "github.com/Sirupsen/logrus"
	ays "github.com/g8os/grid/api/ays-client"
	"github.com/g8os/grid/api/node"
	"github.com/g8os/grid/api/storagecluster"
	"github.com/g8os/grid/api/tools"
	"github.com/g8os/grid/api/volume"
	"github.com/gorilla/handlers"
	"github.com/gorilla/mux"
)

func LoggingMiddleware(h http.Handler) http.Handler {
	return handlers.LoggingHandler(log.StandardLogger().Out, h)
}

type Router struct {
	handler http.Handler
}

type Middleware func(h http.Handler) http.Handler

func NewRouter(h http.Handler) *Router {
	return &Router{
		handler: h,
	}
}

func (i *Router) Use(middlewares ...Middleware) {
	for _, middleware := range middlewares {
		i.handler = middleware(i.handler)
	}
}

func (i *Router) Handler() http.Handler {
	return i.handler
}

func GetRouter(aysURL, aysRepo string) http.Handler {
	r := mux.NewRouter()

	aysAPI := ays.NewAtYourServiceAPI()
	aysAPI.BaseURI = aysURL
	tools.SetAYSClient(aysAPI)

	// home page
	r.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		http.ServeFile(w, r, "apidocs/index.html")
	})

	// apidocs
	r.PathPrefix("/apidocs/").Handler(http.StripPrefix("/apidocs/", http.FileServer(http.Dir("./apidocs/"))))

	node.NodesInterfaceRoutes(r, node.NewNodeAPI(aysRepo, aysAPI))
	storagecluster.StorageclustersInterfaceRoutes(r, storagecluster.NewStorageClusterAPI(aysRepo, aysAPI))
	volume.VolumesInterfaceRoutes(r, volume.NewVolumeAPI(aysRepo, aysAPI))

	router := NewRouter(r)
	router.Use(LoggingMiddleware)

	return router.Handler()
}
