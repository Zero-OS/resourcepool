package run

type EnumRunState string

const (
	EnumRunStateok        EnumRunState = "ok"
	EnumRunStaterunning   EnumRunState = "running"
	EnumRunStatescheduled EnumRunState = "scheduled"
	EnumRunStateerror     EnumRunState = "error"
	EnumRunStatenew       EnumRunState = "new"
	EnumRunStatedisabled  EnumRunState = "disabled"
	EnumRunStatechanged   EnumRunState = "changed"
)
