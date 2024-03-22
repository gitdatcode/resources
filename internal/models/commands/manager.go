package commands

import (
	"errors"
	"strings"
)

var (
	ErrRegistration    error                  = errors.New(`command already registered`)
	ErrNotFound        error                  = errors.New(`command not found`)
	registeredCommands map[string]Commandable = map[string]Commandable{}
	registeredActions  map[string]Actionable  = map[string]Actionable{}
	helpCommand        string                 = "--help"
)

type ResponseWriter func(content any)

// Register does the work of adding a workable to the global registry as a command
// or an action, or both
func Register(cmd Workable) error {
	if cmdType, ok := cmd.(Commandable); ok {
		_, ok := registeredCommands[cmd.Name()]
		if ok {
			return ErrRegistration
		}

		registeredCommands[cmd.Name()] = cmdType
	}

	if actType, ok := cmd.(Actionable); ok {
		_, ok := registeredActions[cmd.Name()]
		if ok {
			return ErrRegistration
		}

		registeredActions[cmd.Name()] = actType
	}

	return nil
}

// Command will execute a registered command's Command method. The args slice will include
// the name of the command and any space separated strings. If the length
// of args is 2 and the last index is the word "help" the help string will
// be returned for the command. Otherwise the Command method is called
// against the command
func Command(resp ResponseWriter, slashCommand SlashCommand) error {
	sCmd := strings.TrimLeft(slashCommand.Command, "/")
	cmd, ok := registeredCommands[sCmd]
	if !ok {
		return ErrNotFound
	}

	if strings.HasPrefix(slashCommand.Text, helpCommand) {
		resp(cmd.Help())
		return nil
	}

	return cmd.Command(resp, slashCommand)
}

// ExecuteAction will execute a registered command' Action. The args slice will include
// the name of the command and any space separated strings. If the length
// of args is 2 and the last index is the word "help" the help string will
// be returned for the command. Otherwise the Action method is called
// against the command
func ExecuteAction(resp ResponseWriter, dialogSubmission DialogSubmission[GenericReponse]) error {
	aCmd := strings.Split(dialogSubmission.CallBackID, "/")
	action, ok := registeredActions[aCmd[0]]
	if !ok {
		return ErrNotFound
	}

	return action.Action(resp, dialogSubmission)
}
