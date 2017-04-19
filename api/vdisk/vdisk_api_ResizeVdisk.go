package vdisk

import (
	"encoding/json"
	"fmt"
	"net/http"

	log "github.com/Sirupsen/logrus"

	"github.com/g8os/grid/api/tools"
	"github.com/gorilla/mux"
)

// ResizeVdisk is the handler for POST /vdisks/{vdiskid}/resize
// Resize Vdisk
func (api VdisksAPI) ResizeVdisk(w http.ResponseWriter, r *http.Request) {
	var reqBody VdiskResize

	vdiskID := mux.Vars(r)["vdiskid"]

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

	// Create resize blueprint
	bp := struct {
		Size int `yaml:"size" json:"size"`
	}{
		Size: reqBody.NewSize,
	}

	decl := fmt.Sprintf("vdisk__%v", vdiskID)

	obj := make(map[string]interface{})
	obj[decl] = bp
	obj["actions"] = []map[string]string{map[string]string{"action": "resize"}}

	// And execute
	if _, err := tools.ExecuteBlueprint(api.AysRepo, "vdisk", vdiskID, "resize", obj); err != nil {
		log.Errorf("error executing blueprint for vdisk %s resize : %+v", vdiskID, err)
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}
