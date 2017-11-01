package router

import (
	"bytes"
	"net/http"
	"time"

	log "github.com/Sirupsen/logrus"
	"github.com/gorilla/handlers"
	"github.com/gorilla/mux"
	cache "github.com/patrickmn/go-cache"
	"github.com/zero-os/0-orchestrator/api/backup"
	"github.com/zero-os/0-orchestrator/api/graph"
	"github.com/zero-os/0-orchestrator/api/healthcheck"
	"github.com/zero-os/0-orchestrator/api/node"
	"github.com/zero-os/0-orchestrator/api/storagecluster"
	"github.com/zero-os/0-orchestrator/api/tools"
	"github.com/zero-os/0-orchestrator/api/vdiskstorage"
	"github.com/zero-os/0-orchestrator/api/vdiskstorage/vdisk"
	"github.com/zero-os/0-orchestrator/api/webhook"
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

func GetRouter(aysURL, aysRepo, aysRetries, org string, jwtProvider *tools.JWTProvider) http.Handler {
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

	apihandler := adapt(api, tools.NewOauth2itsyouonlineMiddleware(org).Handler, tools.ConnectionMiddleware(), LoggingMiddleware)

	r.PathPrefix("/nodes").Handler(apihandler)
	r.PathPrefix("/graphs").Handler(apihandler)
	r.PathPrefix("/storageclusters").Handler(apihandler)
	r.PathPrefix("/health").Handler(apihandler)
	r.PathPrefix("/backup").Handler(apihandler)
	r.PathPrefix("/vdiskstorage").Handler(apihandler)
	r.PathPrefix("/webhooks").Handler(apihandler)

	node.NodesInterfaceRoutes(api, node.NewNodeAPI(aysRepo, aysURL, aysRetries, jwtProvider, cache.New(5*time.Minute, 1*time.Minute)))
	graph.GraphsInterfaceRoutes(api, graph.NewGraphAPI(aysRepo, aysURL, aysRetries, jwtProvider, cache.New(5*time.Minute, 1*time.Minute)))
	storagecluster.StorageclustersInterfaceRoutes(api, storagecluster.NewStorageClusterAPI(aysRepo, aysURL, aysRetries, jwtProvider))
	vdisk.VdisksInterfaceRoutes(api, vdisk.NewVdiskAPI(aysRepo, aysURL, aysRetries, jwtProvider))
	healthcheck.HealthChechInterfaceRoutes(api, healthcheck.NewHealthCheckAPI(aysRepo, aysURL, aysRetries, jwtProvider))
	backup.BackupInterfaceRoutes(api, backup.NewBackupAPI(aysRepo, aysURL, aysRetries, jwtProvider))
	vdiskstorage.VdiskstorageInterfaceRoutes(api, vdiskstorage.NewVdiskStorageAPI(aysRepo, aysURL, aysRetries, jwtProvider))
	webhook.WebhooksInterfaceRoutes(api, webhook.NewWebhookAPI(aysRepo, aysURL, aysRetries, jwtProvider))

	return r
}
