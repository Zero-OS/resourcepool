package node

import (
	"encoding/json"
	"net/http"

	"strconv"
	"strings"

	"github.com/g8os/go-client"
	"github.com/g8os/resourcepool/api/tools"
	psdisk "github.com/shirou/gopsutil/disk"
)

// GetDiskInfo is the handler for GET /nodes/{nodeid}/disk
// Get detailed information of all the disks in the node
func (api NodeAPI) GetDiskInfo(w http.ResponseWriter, r *http.Request) {
	cl, err := tools.GetConnection(r, api)
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	disk := client.Disk(cl)
	result, err := disk.List()
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	info := client.Info(cl)
	mountedDisks, err := info.Disk()
	if err != nil {
		tools.WriteError(w, http.StatusInternalServerError, err)
		return
	}

	mountedDisksMap := make(map[string]psdisk.PartitionStat, len(mountedDisks))

	for _, mountedDisk := range mountedDisks {
		mountedDisksMap[mountedDisk.Mountpoint] = mountedDisk
	}

	var respBody []DiskInfo

	for _, disk := range result.BlockDevices {
		var diskInfo DiskInfo

		device := []string{"/dev", disk.Name}
		diskInfo.Device = strings.Join(device, "/")
		diskInfo.Fstype = disk.Fstype

		if disk.Mountpoint != "" {
			diskInfo.Mountpoint = disk.Mountpoint
			mDisk, ok := mountedDisksMap[disk.Mountpoint]
			if ok {
				diskInfo.Opts = mDisk.Opts
			}
		}

		size, err := strconv.Atoi(disk.Size)
		if err != nil {
			tools.WriteError(w, http.StatusInternalServerError, err)
			return
		}

		diskInfo.Size = size / (1024 * 1024 * 1024) // Convert the size to GB

		if disk.Rota == "1" {
			// Assume that if a disk is more than 7TB it's a SMR disk
			if diskInfo.Size > (1024 * 7) {
				diskInfo.Type = EnumDiskInfoTypearchive
			} else {
				diskInfo.Type = EnumDiskInfoTypehdd
			}
		} else {
			if strings.Contains(disk.Name, "nvme") {
				diskInfo.Type = EnumDiskInfoTypenvme
			} else {
				diskInfo.Type = EnumDiskInfoTypessd
			}
		}
		respBody = append(respBody, diskInfo)
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
