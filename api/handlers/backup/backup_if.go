package backup

import (
	"net/http"

	"github.com/gorilla/mux"
)

// BackupInterface is interface for /backup root endpoint
type BackupInterface interface {
	// Create a backup
	Create(http.ResponseWriter, *http.Request)
	// List backups
	List(http.ResponseWriter, *http.Request)
}

// BackupInterfaceRoutesis routing for /backup root endpoint
func BackupInterfaceRoutes(r *mux.Router, i BackupInterface) {
	r.HandleFunc("/backup", i.Create).Methods("POST")
	r.HandleFunc("/backup", i.List).Methods("GET")
}
