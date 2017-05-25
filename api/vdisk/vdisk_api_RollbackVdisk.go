package vdisk

import (
	"encoding/json"
	"net/http"

	"github.com/g8os/resourcepool/api/tools"
)

// RollbackVdisk is the handler for POST /vdisks/{vdiskid}/rollback
// Rollback a vdisk to a previous state
func (api VdisksAPI) RollbackVdisk(w http.ResponseWriter, r *http.Request) {
	var reqBody VdiskRollback

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err)
		return
	}

	// validate request
	if err := reqBody.Validate(); err != nil {
		tools.WriteError(w, http.StatusBadRequest, err)
		return
	}

	// Create rollback blueprint
	// TODO: define rollback
	// vdiskId := mux.Vars(r)["vdiskid"]
	// bp := struct {
	// 	Epoch int `yaml:"epoch" json:"epoch"`
	// }{
	// 	Epoch: reqBody.Epoch,
	// }
	//
	// bpName := fmt.Sprintf("vdiskrollback%sfrom%vto%v", vdiskId, time.Now().Unix(), reqBody.Epoch)
	// decl := fmt.Sprintf("vdisk__%v", vdiskId)
	//
	// obj := make(map[string]interface{})
	// obj[decl] = bp
	// obj["actions"] = []map[string]string{map[string]string{"action": "rollback"}}
	//
	// // And execute
	// if _, err := tools.ExecuteBlueprint(api.AysRepo, bpName, obj); err != nil {
	// 	log.Errorf("error executing blueprint for vdisk %s rollback : %+v", vdiskId, err)
	// 	tools.WriteError(w, http.StatusInternalServerError, err)
	// 	return
	// }
	//
	// w.WriteHeader(http.StatusNoContent)
}
