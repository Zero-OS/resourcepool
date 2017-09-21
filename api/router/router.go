package router

import (
	"bytes"
	"net/http"
	"time"

	log "github.com/Sirupsen/logrus"
	"github.com/gorilla/handlers"
	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/ays"
	"github.com/zero-os/0-orchestrator/api/graph"
	"github.com/zero-os/0-orchestrator/api/storagecluster"
	"github.com/zero-os/0-orchestrator/api/tools"
	"github.com/zero-os/0-orchestrator/api/vdisk"
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

// func GetRouter(aysURL, aysRepo, cbMgr callback.Mgr, org string, applicationID string, secret string) http.Handler {
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
	// apihandler := adapt(api, tools.NewOauth2itsyouonlineMiddleware(org).Handler, tools.ConnectionMiddleware(), LoggingMiddleware)
	cbHandler := adapt(api, LoggingMiddleware)

	r.PathPrefix("/nodes").Handler(apihandler)
	r.PathPrefix("/graphs").Handler(apihandler)
	r.PathPrefix("/vdisks").Handler(apihandler)
	r.PathPrefix("/storageclusters").Handler(apihandler)
	r.PathPrefix("/health").Handler(apihandler)
	r.PathPrefix("/backup").Handler(apihandler)

	// node.NodesInterfaceRoutes(api, node.NewNodeAPI(aysRepo, aysURL, applicationID, secret, org, cache.New(5*time.Minute, 1*time.Minute)), org)
	// graph.GraphsInterfaceRoutes(api, graph.NewGraphAPI(aysRepo, aysURL, applicationID, secret, org, cache.New(5*time.Minute, 1*time.Minute)), org)
	// storagecluster.StorageclustersInterfaceRoutes(api, storagecluster.NewStorageClusterAPI(aysRepo, aysURL, applicationID, secret, org), org)
	// vdisk.VdisksInterfaceRoutes(api, vdisk.NewVdiskAPI(aysRepo, aysURL, applicationID, secret, org), org)
	// healthcheck.HealthChechInterfaceRoutes(api, healthcheck.NewHealthcheckAPI(aysRepo, aysURL, applicationID, secret, org), org)
	// backup.BackupInterfaceRoutes(api, backup.NewBackupAPI(aysRepo, aysURL, applicationID, secret, org), org)

	// node.NodesInterfaceRoutes(api, node.NewNodeAPI(aysCL, cache.New(5*time.Minute, 1*time.Minute)), org)
	graph.GraphsInterfaceRoutes(api, graph.NewGraphAPI(aysCl))
	storagecluster.StorageclustersInterfaceRoutes(api, storagecluster.NewStorageClusterAPI(aysCl))
	vdisk.VdisksInterfaceRoutes(api, vdisk.NewVdiskAPI(aysCl))
	// healthcheck.HealthChechInterfaceRoutes(api, healthcheck.NewHealthcheckAPI(aysRepo, aysURL, applicationID, secret, org), org)
	// backup.BackupInterfaceRoutes(api, backup.NewBackupAPI(aysRepo, aysURL, applicationID, secret, org), org)

	r.PathPrefix("/callback").Handler(cbHandler)
	api.HandleFunc("/callback", aysCl.CallbackHandler()).Methods("POST")

	return r
}
