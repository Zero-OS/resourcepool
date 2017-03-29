package main

type EnumStorageServerStatus string

const (
	EnumStorageServerStatusready EnumStorageServerStatus = "ready"
	EnumStorageServerStatuserror EnumStorageServerStatus = "error"
)
