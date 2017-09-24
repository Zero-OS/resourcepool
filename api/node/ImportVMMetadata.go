package node

type ImportVMMetadata struct {
	CPU         int         `yaml:"cpu" json:"cpu" validate:"nonzero"`
	CryptoKey   string      `yaml:"cryptoKey" json:"cryptoKey" validate:"nonzero"`
	Disks       []VDiskLink `yaml:"disks" json:"disks"`
	Memory      int         `yaml:"memory" validate:"nonzero" validate:"nonzero"`
	Nics        []NicLink   `yaml:"nics"`
	SnapshotIDs []string    `yaml:"snapshotIDs"`
	Vdisks      []Vdisk     `yaml:"vdisks"`
}

type Vdisk struct {
	Blocksize int    `yaml:"blockSize" json:"blockSize" validate:"nonzero"`
	ReadOnly  bool   `yaml:"readOnly" json:"readOnly,omitempty"`
	Size      int    `yaml:"size" json:"size" validate:"nonzero"`
	Vdisktype string `yaml:"type" json:"type" validate:"nonzero"`
	ID        string `yaml:"id" json:"id" validate:"nonzero"`
}
