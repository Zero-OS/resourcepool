package main

type EnumNicLinkType string

const (
	EnumNicLinkTypevlan     EnumNicLinkType = "vlan"
	EnumNicLinkTypevxlan    EnumNicLinkType = "vxlan"
	EnumNicLinkTypezerotier EnumNicLinkType = "zerotier"
)
