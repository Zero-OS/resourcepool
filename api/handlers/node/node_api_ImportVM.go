package node

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"strings"
	"time"

	yaml "gopkg.in/yaml.v2"

	log "github.com/Sirupsen/logrus"
	"github.com/gorilla/mux"
	"github.com/jlaffaye/ftp"

	"github.com/zero-os/0-orchestrator/api/httperror"
	tools "github.com/zero-os/0-orchestrator/api/tools"
)

// ImportVM is the handler for POST /nodes/{nodeid}/vms/{vmid}/import
// Import the VM
func (api *NodeAPI) ImportVM(w http.ResponseWriter, r *http.Request) {
	aysClient := tools.GetAysConnection(r, api)

	vars := mux.Vars(r)
	vmID := vars["vmid"]
	nodeID := vars["nodeid"]

	var reqBody ImportVM

	// decode request
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		httperror.WriteError(w, http.StatusBadRequest, err, "Error decoding request body")
		return
	}
	reqBody.URL = strings.TrimRight(reqBody.URL, "/")

	// validate request
	if err := reqBody.Validate(); err != nil {
		httperror.WriteError(w, http.StatusBadRequest, err, "")
		return
	}

	// valdiate name
	exists, err := aysClient.ServiceExists("vm", vmID, api.AysRepo)
	if exists {
		err = fmt.Errorf("VM with name %s already exists", vmID)
		httperror.WriteError(w, http.StatusConflict, err, err.Error())
		return
	}

	ftpinfo := GetFtpInfo(reqBody.URL)

	cl, err := ftp.Dial(ftpinfo.Host)
	if err != nil {
		err = fmt.Errorf("Could not connect to %s", reqBody.URL)
		httperror.WriteError(w, http.StatusBadRequest, err, err.Error())
		return
	}

	err = cl.Login(ftpinfo.Username, ftpinfo.Passwd)
	if err != nil {
		err = fmt.Errorf("Could not login to %s", reqBody.URL)
		httperror.WriteError(w, http.StatusBadRequest, err, err.Error())
		return
	}

	res, err := cl.Retr(ftpinfo.Path)
	if err != nil {
		err = fmt.Errorf("Could not retrieve to %s from the ftp server", ftpinfo.Path)
		httperror.WriteError(w, http.StatusBadRequest, err, err.Error())
		return
	}

	buf, err := ioutil.ReadAll(res)
	res.Close()
	if err != nil {
		log.Error(err.Error())
		err = fmt.Errorf("Failed to read %s", ftpinfo.Path)
		httperror.WriteError(w, http.StatusInternalServerError, err, err.Error())
		return
	}

	var metadata ImportVMMetadata
	err = yaml.Unmarshal([]byte(buf), &metadata)
	if err != nil {
		log.Error(err.Error())
		err = fmt.Errorf("Invalid metadata to import vm %s", ftpinfo.Path)
		httperror.WriteError(w, http.StatusInternalServerError, err, err.Error())
		return
	}

	vdiskServices := []string{}
	for idx, val := range metadata.Vdisks {
		backupURL := fmt.Sprintf("%s#%s#%s", reqBody.URL, metadata.CryptoKey, metadata.SnapshotIDs[idx])
		// Create the blueprint
		bp := struct {
			Size                 int    `yaml:"size" json:"size"`
			BlockSize            int    `yaml:"blocksize" json:"blocksize"`
			ReadOnly             bool   `yaml:"readOnly" json:"readOnly"`
			Type                 string `yaml:"type" json:"type"`
			BackupURL            string `yaml:"backupUrl" json:"backupUrl"`
			BlockStoragecluster  string `yaml:"blockStoragecluster" json:"blockStoragecluster"`
			ObjectStoragecluster string `yaml:"objectStoragecluster" json:"objectStoragecluster"`
			BackupStoragecluster string `yaml:"backupStoragecluster" json:"backupStoragecluster"`
		}{
			Size:                 val.Size,
			BlockSize:            val.Blocksize,
			ReadOnly:             val.ReadOnly,
			Type:                 string(val.Vdisktype),
			BlockStoragecluster:  reqBody.BlockStoragecluster,
			ObjectStoragecluster: reqBody.ObjectStoragecluster,
			BackupStoragecluster: reqBody.BackupStoragecluster,
			BackupURL:            backupURL,
		}

		now := time.Now()
		serviceName := fmt.Sprintf("%s_%v", vmID, now.Unix())
		vdiskServices = append(vdiskServices, serviceName)
		bpName := fmt.Sprintf("vdisk__%v", serviceName)

		obj := make(map[string]interface{})
		obj[bpName] = bp
		obj["actions"] = []tools.ActionBlock{{Action: "import_vdisk", Service: serviceName, Actor: "vdisk"}}

		res, err := aysClient.ExecuteBlueprint(api.AysRepo, "vdisk", vmID, "import_vdisk", obj)
		errmsg := fmt.Sprintf("error executing blueprint for vm %s import", vmID)
		if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
			return
		}

		if _, err := aysClient.WaitRunDone(res.Key, api.AysRepo); err != nil {
			httpErr, ok := err.(httperror.HTTPError)
			if ok {
				httperror.WriteError(w, httpErr.Resp.StatusCode, httpErr, "")
			} else {
				httperror.WriteError(w, http.StatusInternalServerError, err, errmsg)
			}
			return
		}
	}

	// Change diskids with new ones
	var disks []VDiskLink
	for idx, val := range metadata.Disks {
		val.Vdiskid = vdiskServices[idx]
		disks = append(disks, val)
	}

	// Create vm
	bp := struct {
		Node      string      `yaml:"node" json:"node"`
		Memory    int         `yaml:"memory" json:"memory"`
		CPU       int         `yaml:"cpu" json:"cpu"`
		Nics      []NicLink   `yaml:"nics" json:"nics"`
		Disks     []VDiskLink `yaml:"disks" json:"disks"`
		BackupURL string      `yaml:"backupUrl" json:"backupUrl"`
	}{
		Node:      nodeID,
		Memory:    metadata.Memory,
		CPU:       metadata.CPU,
		Nics:      metadata.Nics,
		Disks:     disks,
		BackupURL: "",
	}

	obj := make(map[string]interface{})
	obj[fmt.Sprintf("vm__%s", vmID)] = bp
	obj["actions"] = []tools.ActionBlock{{Service: vmID, Actor: "vm", Action: "install"}}

	run, err := aysClient.ExecuteBlueprint(api.AysRepo, "vm", vmID, "install", obj)
	errmsg := fmt.Sprintf("error executing blueprint for vm %s creation", vmID)
	if !tools.HandleExecuteBlueprintResponse(err, w, errmsg) {
		return
	}

	if _, errr := aysClient.WaitOnRun(w, api.AysRepo, run.Key); errr != nil {
		return
	}

	w.Header().Set("Location", fmt.Sprintf("/nodes/%s/vms/%s", nodeID, vmID))
	w.WriteHeader(http.StatusCreated)
}
