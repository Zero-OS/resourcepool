import requests


from .Bridge import Bridge
from .BridgeCreate import BridgeCreate
from .BridgeCreateSetting import BridgeCreateSetting
from .CPUInfo import CPUInfo
from .CPUStats import CPUStats
from .CloudInit import CloudInit
from .Cluster import Cluster
from .ClusterCreate import ClusterCreate
from .Container import Container
from .ContainerListItem import ContainerListItem
from .ContainerNIC import ContainerNIC
from .CoreStateResult import CoreStateResult
from .CoreSystem import CoreSystem
from .CreateContainer import CreateContainer
from .CreateSnapshotReqBody import CreateSnapshotReqBody
from .DHCP import DHCP
from .DeleteFile import DeleteFile
from .DiskInfo import DiskInfo
from .DiskPartition import DiskPartition
from .EnumBridgeCreateNetworkMode import EnumBridgeCreateNetworkMode
from .EnumBridgeStatus import EnumBridgeStatus
from .EnumClusterCreateDriveType import EnumClusterCreateDriveType
from .EnumClusterDriveType import EnumClusterDriveType
from .EnumClusterStatus import EnumClusterStatus
from .EnumContainerListItemStatus import EnumContainerListItemStatus
from .EnumContainerNICStatus import EnumContainerNICStatus
from .EnumContainerNICType import EnumContainerNICType
from .EnumContainerStatus import EnumContainerStatus
from .EnumDiskInfoType import EnumDiskInfoType
from .EnumGWNICType import EnumGWNICType
from .EnumJobResultName import EnumJobResultName
from .EnumJobResultState import EnumJobResultState
from .EnumNicLinkType import EnumNicLinkType
from .EnumNodeStatus import EnumNodeStatus
from .EnumStoragePoolCreateDataProfile import EnumStoragePoolCreateDataProfile
from .EnumStoragePoolCreateMetadataProfile import EnumStoragePoolCreateMetadataProfile
from .EnumStoragePoolDataProfile import EnumStoragePoolDataProfile
from .EnumStoragePoolDeviceStatus import EnumStoragePoolDeviceStatus
from .EnumStoragePoolListItemStatus import EnumStoragePoolListItemStatus
from .EnumStoragePoolMetadataProfile import EnumStoragePoolMetadataProfile
from .EnumStoragePoolStatus import EnumStoragePoolStatus
from .EnumStorageServerStatus import EnumStorageServerStatus
from .EnumVMListItemStatus import EnumVMListItemStatus
from .EnumVMStatus import EnumVMStatus
from .EnumVdiskCreateType import EnumVdiskCreateType
from .EnumVdiskListItemStatus import EnumVdiskListItemStatus
from .EnumVdiskListItemType import EnumVdiskListItemType
from .EnumVdiskStatus import EnumVdiskStatus
from .EnumVdiskType import EnumVdiskType
from .EnumZerotierListItemType import EnumZerotierListItemType
from .EnumZerotierType import EnumZerotierType
from .Filesystem import Filesystem
from .FilesystemCreate import FilesystemCreate
from .GW import GW
from .GWCreate import GWCreate
from .GWHost import GWHost
from .GWNIC import GWNIC
from .HTTPProxy import HTTPProxy
from .HTTPType import HTTPType
from .IPProtocol import IPProtocol
from .Job import Job
from .JobListItem import JobListItem
from .JobResult import JobResult
from .MemInfo import MemInfo
from .NicInfo import NicInfo
from .NicLink import NicLink
from .Node import Node
from .NodeMount import NodeMount
from .OSInfo import OSInfo
from .PortForward import PortForward
from .Process import Process
from .ProcessSignal import ProcessSignal
from .Snapshot import Snapshot
from .StoragePool import StoragePool
from .StoragePoolCreate import StoragePoolCreate
from .StoragePoolDevice import StoragePoolDevice
from .StoragePoolListItem import StoragePoolListItem
from .StorageServer import StorageServer
from .VDiskLink import VDiskLink
from .VM import VM
from .VMCreate import VMCreate
from .VMDiskInfo import VMDiskInfo
from .VMInfo import VMInfo
from .VMListItem import VMListItem
from .VMMigrate import VMMigrate
from .VMNicInfo import VMNicInfo
from .VMUpdate import VMUpdate
from .Vdisk import Vdisk
from .VdiskCreate import VdiskCreate
from .VdiskListItem import VdiskListItem
from .VdiskResize import VdiskResize
from .VdiskRollback import VdiskRollback
from .WriteFile import WriteFile
from .Zerotier import Zerotier
from .ZerotierJoin import ZerotierJoin
from .ZerotierListItem import ZerotierListItem
from .ZerotierRoute import ZerotierRoute

from .client import Client as APIClient


class Client:
    def __init__(self, base_uri=""):
        self.api = APIClient(base_uri)
        