package vdisk

import (
	"net/http"
)

// TODO: review this flow

// CreateNewVdisk is the handler for POST /vdisks
// Create a new vdisk, can be a copy from an existing vdisk
func (api *VdisksAPI) CreateNewVdisk(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)
	// var reqBody VdiskCreate
	// vars := mux.Vars(r)
	// vdiskStoreID := vars["vdiskstorageid"]
	// // var vdiskstore vdiskstorage.VdiskStorage

	// // decode request
	// if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
	// 	tools.WriteError(w, http.StatusBadRequest, err, "Error decoding request body")
	// 	return
	// }

	// // get vdiskstorage

	// // validate request
	// if err := reqBody.Validate(); err != nil {
	// 	tools.WriteError(w, http.StatusBadRequest, err, "")
	// 	return
	// }

	// exists, err := aysClient.ServiceExists("vdisk", reqBody.ID, api.AysRepo)
	// if err != nil {
	// 	errmsg := fmt.Sprintf("error getting vdisk service by name %s ", reqBody.ID)
	// 	tools.WriteError(w, http.StatusInternalServerError, err, errmsg)
	// 	return
	// }
	// if exists {
	// 	tools.WriteError(w, http.StatusConflict, fmt.Errorf("A vdisk with ID %s already exists", reqBody.ID), "")
	// 	return
	// }

	// // get vdisk service
	// // service, resp, err := aysClient.Ays.GetServiceByName(reqBody.VdiskStorage, "vdiskstorage", api.AysRepo, nil, nil)
	// // if !tools.HandleAYSResponse(err, resp, w, fmt.Sprintf("getting vdiskstorage %s service", reqBody.VdiskStorage)) {
	// // 	return
	// // }
	// // // unmarshal service data
	// // if err := json.Unmarshal(service.Data, &vdiskstore); err != nil {
	// // 	tools.WriteError(w, http.StatusInternalServerError, err, "error unmarshaling vdiskstorage service data")
	// // 	return
	// // }

	// // Create the blueprint
	// bp := struct {
	// 	Size          int    `yaml:"size" json:"size"`
	// 	BlockSize     int    `yaml:"blocksize" json:"blocksize"`
	// 	TemplateVdisk string `yaml:"templateVdisk" json:"templateVdisk"`
	// 	ReadOnly      bool   `yaml:"readOnly" json:"readOnly"`
	// 	Type          string `yaml:"type" json:"type"`
	// 	VdiskStorage  string `yaml:"vdiskstorage" json:"vdiskstorage"`
	// }{
	// 	Size:          reqBody.Size,
	// 	BlockSize:     reqBody.Blocksize,
	// 	TemplateVdisk: reqBody.Templatevdisk,
	// 	ReadOnly:      reqBody.ReadOnly,
	// 	Type:          string(reqBody.Vdisktype),
	// 	VdiskStorage:  reqBody.VdiskStorage,
	// }

	// bpName := fmt.Sprintf("vdisk__%s", reqBody.ID)

	// obj := make(map[string]interface{})
	// obj[bpName] = bp
	// obj["actions"] = []tools.ActionBlock{{Action: "install", Service: reqBody.ID, Actor: "vdisk"}}

	// // And Execute

	// run, err := aysClient.ExecuteBlueprint(api.AysRepo, "vdisk", reqBody.ID, "install", obj)
	// errmsg := fmt.Sprintf("error executing blueprint for vdisk %s creation", reqBody.ID)
	// if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
	// 	return
	// }

	// if _, errr := tools.WaitOnRun(api, w, r, run.Key); errr != nil {
	// 	return
	// }
	// w.Header().Set("Location", fmt.Sprintf("/vdisks/%s", reqBody.ID))
	// w.WriteHeader(http.StatusCreated)
}
