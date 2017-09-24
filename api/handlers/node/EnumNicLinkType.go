package node

type EnumNicLinkType string

const (
	EnumNicLinkTypevlan    EnumNicLinkType = "vlan"
	EnumNicLinkTypevxlan   EnumNicLinkType = "vxlan"
	EnumNicLinkTypedefault EnumNicLinkType = "default"
	EnumNicLinkTypebridge  EnumNicLinkType = "bridge"
)
