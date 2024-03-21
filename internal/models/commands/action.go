package commands

type Workable interface {
	Name() string
	Help() string
}

type Commandable interface {
	Workable
	Command(resp ResponseWriter, args ...string) error
}

type Actionable interface {
	Workable
	Action(resp ResponseWriter, args ...string) error
}
