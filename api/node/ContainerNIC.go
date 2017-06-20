package node

type ContainerNICConfig struct {
	Dhcp    bool     `json:"dhcp"`
	Cidr    string   `json:"cidr"`
	Gateway string   `json:"gateway"`
	DNS     []string `json:"dns"`
}

type ContainerNIC struct {
	BaseNic `yaml:",inline"`
	Config  ContainerNICConfig `json:"config,omitempty" yaml:"config,omitempty"`
	Hwaddr  string             `json:"hwaddr,omitempty" yaml:"hwaddr,omitempty" validate:"macaddress=empty"`
}
