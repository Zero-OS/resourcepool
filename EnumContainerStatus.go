package main

type EnumContainerStatus string

const (
	EnumContainerStatusrunning EnumContainerStatus = "running"
	EnumContainerStatushalted  EnumContainerStatus = "halted"
)
