package node

import (
	"encoding/json"
	"net/http"

	client "github.com/g8os/grid/api/ays-client"
	"github.com/g8os/grid/api/tools"
)

// ListBridges is the handler for GET /node/{nodeid}/bridge
// List bridges
func (api NodeAPI) ListBridges(w http.ResponseWriter, r *http.Request) {
	var respBody []Bridge
	json.NewEncoder(w).Encode(&respBody)
	cl := client.NewAtYourServiceAPI()
	_, resp, err := cl.Ays.ListServicesByRole("bridge", api.AysRepo, nil, nil)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}
	if resp.StatusCode != http.StatusOK {
		w.WriteHeader(resp.StatusCode)
		return
	}
}
