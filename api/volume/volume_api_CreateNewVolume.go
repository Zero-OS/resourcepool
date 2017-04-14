package volume

import (
	"encoding/json"
	"fmt"
	"net/http"

	log "github.com/Sirupsen/logrus"

	"github.com/g8os/grid/api/tools"
)

// CreateNewVolume is the handler for POST /volumes
// Create a new volume, can be a copy from an existing volume
func (api VolumesAPI) CreateNewVolume(w http.ResponseWriter, r *http.Request) {
	var reqBody VolumeCreate

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		w.WriteHeader(400)
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		w.WriteHeader(400)
		w.Write([]byte(`{"error":"` + err.Error() + `"}`))
		return
	}

	_, resp, _ := api.AysAPI.Ays.GetServiceByName(reqBody.ID, "volume", api.AysRepo, nil, nil)
	if resp.StatusCode != http.StatusNotFound {
		tools.WriteError(w, http.StatusConflict, fmt.Errorf("A volume with ID %s already exists", reqBody.ID))
		return
	}

	// Create the blueprint
	bp := struct {
		Size           int    `yaml:"size" json:"size"`
		BlockSize      int    `yaml:"blocksize" json:"blocksize"`
		TemplateVolume string `yaml:"templateVolume" json:"templateVolume"`
		ReadOnly       bool   `yaml:"readOnly" json:"readOnly"`
		Type           string `yaml:"type" json:"type"`
		StorageCluster string `yaml:"storageCluster" json:"storageCluster"`
	}{
		Size:           reqBody.Size,
		BlockSize:      reqBody.Blocksize,
		TemplateVolume: reqBody.Templatevolume,
		ReadOnly:       reqBody.ReadOnly,
		Type:           string(reqBody.Volumetype),
		StorageCluster: reqBody.Storagecluster,
	}

	bpName := fmt.Sprintf("volume__%s", reqBody.ID)

	obj := make(map[string]interface{})
	obj[bpName] = bp
	obj["actions"] = []tools.ActionBlock{{"action": "install"}}

	// And Execute
	if _, err := tools.ExecuteBlueprint(api.AysRepo, "volume", reqBody.ID, "install", obj); err != nil {
		log.Errorf("error executing blueprint for volume %s creation : %+v", reqBody.ID, err)
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	w.Header().Set("Location", fmt.Sprintf("/volumes/%s", reqBody.ID))
	w.WriteHeader(http.StatusCreated)
}
