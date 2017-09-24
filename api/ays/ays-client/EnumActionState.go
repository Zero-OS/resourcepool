package client

type EnumActionState string

const (
	EnumActionStatenew       EnumActionState = "new"
	EnumActionStatechanged   EnumActionState = "changed"
	EnumActionStateok        EnumActionState = "ok"
	EnumActionStatescheduled EnumActionState = "scheduled"
	EnumActionStatedisabled  EnumActionState = "disabled"
	EnumActionStateerror     EnumActionState = "error"
	EnumActionStaterunning   EnumActionState = "running"
)
