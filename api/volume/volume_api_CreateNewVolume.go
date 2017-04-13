package volume

import (
	"crypto/rand"
	"encoding/base32"
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

	byteSecret, err := generateRandomBytes(32)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}
	name := base32.StdEncoding.EncodeToString(byteSecret)
	vName := fmt.Sprintf("v%v", name)
	bpName := fmt.Sprintf("volume__%v", vName)

	obj := make(map[string]interface{})
	obj[bpName] = bp
	obj["actions"] = []map[string]string{map[string]string{"action": "install"}}

	// And Execute
	if _, err := tools.ExecuteBlueprint(api.AysRepo, "volume", vName, "install", obj); err != nil {
		log.Errorf("error executing blueprint for volume %v creation : %+v", vName, err)
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	w.Header().Set("Location", fmt.Sprintf("/volumes/%v", vName))
	w.WriteHeader(http.StatusCreated)
}

func generateRandomBytes(length int) ([]byte, error) {
	b := make([]byte, length)
	_, err := rand.Read(b)
	if err != nil {
		return b, err
	}
	return b, nil
}
