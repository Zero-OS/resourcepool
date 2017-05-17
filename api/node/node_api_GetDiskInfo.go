package node

import (
	"encoding/json"
	"net/http"

	"strconv"
	"strings"

	"fmt"

	"github.com/g8os/go-client"
	"github.com/g8os/resourcepool/api/tools"
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

	var respBody []DiskInfo

	for _, disk := range result.BlockDevices {
		diskInfo := DiskInfo{
			Device:     fmt.Sprintf("/dev/%v", disk.Name),
			Partitions: []DiskPartition{},
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

		for _, partition := range disk.Children {
			diskPartition := DiskPartition{
				Name:     fmt.Sprintf("/dev/%v", partition.Name),
				PartUUID: partition.Partuuid,
				Label:    partition.Label,
				FsType:   partition.Fstype,
			}

			size, err := strconv.Atoi(partition.Size)
			if err != nil {
				tools.WriteError(w, http.StatusInternalServerError, err)
				return
			}

			diskPartition.Size = size / (1024 * 1024 * 1024) // Convert the size to GB

			diskInfo.Partitions = append(diskInfo.Partitions, diskPartition)

		}
		respBody = append(respBody, diskInfo)
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}
