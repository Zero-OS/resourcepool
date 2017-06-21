package router

import (
	"net/http"
	"time"

	log "github.com/Sirupsen/logrus"
	"github.com/gorilla/handlers"
	"github.com/gorilla/mux"
	cache "github.com/patrickmn/go-cache"
	"github.com/zero-os/0-orchestrator/api/node"
	"github.com/zero-os/0-orchestrator/api/storagecluster"
	"github.com/zero-os/0-orchestrator/api/vdisk"
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

func GetRouter(aysURL, aysRepo, org string) http.Handler {
	r := mux.NewRouter()

	// home page
	r.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		http.ServeFile(w, r, "apidocs/index.html")
	})

	node.NodesInterfaceRoutes(r, node.NewNodeAPI(aysRepo, aysURL, cache.New(5*time.Minute, 1*time.Minute)), org)
	storagecluster.StorageclustersInterfaceRoutes(r, storagecluster.NewStorageClusterAPI(aysRepo, aysURL), org)
	vdisk.VdisksInterfaceRoutes(r, vdisk.NewVdiskAPI(aysRepo, aysURL), org)

	router := NewRouter(r)
	router.Use(LoggingMiddleware)

	return router.Handler()
}
