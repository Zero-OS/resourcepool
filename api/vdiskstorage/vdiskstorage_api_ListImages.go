package vdiskstorage

import (
	"encoding/json"
	"net/http"
	"sync"

	ays "github.com/zero-os/0-orchestrator/api/ays-client"
	"github.com/zero-os/0-orchestrator/api/tools"
)

// ListImages is the handler for GET /vdiskstorage/{vdiskstorageid}/images
// List all vdisk images installed in this VdiskStroage
func (api *VdiskstorageAPI) ListImages(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)
	// vdiskstorageID := mux.Vars(r)["vdiskstorageid"]

	services, res, err := aysClient.Ays.ListServicesByRole("vdisk_image", api.AysRepo, nil, nil)
	if !tools.HandleAYSResponse(err, res, w, "listing vdisk_images") {
		return
	}

	var (
		images = make([]Image, len(services))
		errs   = make([]error, len(services))
		wg     = sync.WaitGroup{}
	)
	wg.Add(len(services))
	for i, serviceData := range services {
		go func(i int, serviceData *ays.ServiceData) {
			defer wg.Done()

			service, _, err := aysClient.Ays.GetServiceByName(serviceData.Name, serviceData.Role, api.AysRepo, nil, nil)
			if err != nil {
				errs[i] = err
				return
			}

			var image Image
			if err := json.Unmarshal(service.Data, &image); err != nil {
				errs[i] = err
				return
			}

			image.Name = serviceData.Name
			images[i] = image

		}(i, &serviceData)
	}

	wg.Wait()

	// TODO: concatenate all  errors into one
	for _, err := range errs {
		if err != nil {
			tools.WriteError(w, http.StatusInternalServerError, err, "Error getting list of images")
			return
		}
	}

	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&images)
}
