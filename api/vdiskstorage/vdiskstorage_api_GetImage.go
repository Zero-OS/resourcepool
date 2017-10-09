package vdiskstorage

import (
	"encoding/json"
	"net/http"

	"github.com/gorilla/mux"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// GetImage is the handler for GET /vdiskstorage/{vdiskstorageid}/images/{imageid}
// Get detail about a vdisk image
func (api *VdiskstorageAPI) GetImage(w http.ResponseWriter, r *http.Request) {
	aysClient, err := tools.GetAysConnection(api)
	if err != nil {
		tools.WriteError(w, http.StatusUnauthorized, err, "")
		return
	}
	imageID := mux.Vars(r)["imageid"]
	var image Image

	imageService, resp, err := aysClient.Ays.GetServiceByName(imageID, "vdisk_image", api.AysRepo, nil, nil)
	if !tools.HandleAYSResponse(err, resp, w, "fail to get image service") {
		return
	}

	if err := json.Unmarshal(imageService.Data, &image); err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err, "fail to get image service")
		return
	}
	image.Name = imageID

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&image)
}
