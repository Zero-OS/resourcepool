package main

type EnumBridgeCreateNetworkMode string

const (
	EnumBridgeCreateNetworkModenone    EnumBridgeCreateNetworkMode = "none"
	EnumBridgeCreateNetworkModestatic  EnumBridgeCreateNetworkMode = "static"
	EnumBridgeCreateNetworkModednsmasq EnumBridgeCreateNetworkMode = "dnsmasq"
)
