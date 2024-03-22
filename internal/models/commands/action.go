package commands

type Workable interface {
	Name() string
	Help() string
}

type Commandable interface {
	Workable
	Command(resp ResponseWriter, slashCommand SlashCommand) error
}

type Actionable interface {
	Workable
	Action(resp ResponseWriter, dialogSubmission DialogSubmission[GenericReponse]) error
}
