package router

import (
	"bytes"
	"net/http"
	"time"

	log "github.com/Sirupsen/logrus"
	"github.com/gorilla/handlers"
	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/ays"
	"github.com/zero-os/0-orchestrator/api/handlers/backup"
	"github.com/zero-os/0-orchestrator/api/handlers/graph"
	"github.com/zero-os/0-orchestrator/api/handlers/healthcheck"
	"github.com/zero-os/0-orchestrator/api/handlers/node"
	"github.com/zero-os/0-orchestrator/api/handlers/storagecluster"
	"github.com/zero-os/0-orchestrator/api/handlers/vdisk"
	"github.com/zero-os/0-orchestrator/api/tools"
)

func LoggingMiddleware(h http.Handler) http.Handler {
	return handlers.LoggingHandler(log.StandardLogger().Out, h)
}

func adapt(h http.Handler, adapters ...func(http.Handler) http.Handler) http.Handler {
	for _, adapter := range adapters {
		h = adapter(h)
	}
	return h
}

func GetRouter(aysCl *ays.Client, org string) http.Handler {
	r := mux.NewRouter()
	api := mux.NewRouter()

	// home page
	r.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		data, err := Asset("api.html")
		if err != nil {
			w.WriteHeader(404)
			return
		}
		datareader := bytes.NewReader(data)
		http.ServeContent(w, r, "index.html", time.Now(), datareader)
	})

	apihandler := adapt(api, tools.NewOauth2itsyouonlineMiddleware(org).Handler, LoggingMiddleware)
	cbHandler := adapt(api, LoggingMiddleware)

	r.PathPrefix("/nodes").Handler(apihandler)
	r.PathPrefix("/graphs").Handler(apihandler)
	r.PathPrefix("/vdisks").Handler(apihandler)
	r.PathPrefix("/storageclusters").Handler(apihandler)
	r.PathPrefix("/health").Handler(apihandler)
	r.PathPrefix("/backup").Handler(apihandler)

	node.NodesInterfaceRoutes(api, node.NewNodeAPI(aysCl))
	graph.GraphsInterfaceRoutes(api, graph.NewGraphAPI(aysCl))
	storagecluster.StorageclustersInterfaceRoutes(api, storagecluster.NewStorageClusterAPI(aysCl))
	vdisk.VdisksInterfaceRoutes(api, vdisk.NewVdiskAPI(aysCl))
	healthcheck.HealthChechInterfaceRoutes(api, healthcheck.NewHealthcheckAPI(aysCl))
	backup.BackupInterfaceRoutes(api, backup.NewBackupAPI(aysCl))

	r.PathPrefix("/callback").Handler(cbHandler)
	api.HandleFunc("/callback", aysCl.CallbackHandler()).Methods("POST")

	return r
}
