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
func Command(resp ResponseWriter, args ...string) error {
	cmd, ok := registeredCommands[args[0]]
	if !ok {
		return ErrNotFound
	}

	if len(args) == 2 && strings.TrimSpace(args[1]) == helpCommand {
		resp(cmd.Help())
		return nil
	}

	// drop the command name
	if len(args) > 0 {
		args = args[1:]
	}

	return cmd.Command(resp, args...)
}

// ExecuteAction will execute a registered command' Action. The args slice will include
// the name of the command and any space separated strings. If the length
// of args is 2 and the last index is the word "help" the help string will
// be returned for the command. Otherwise the Action method is called
// against the command
func ExecuteAction(resp ResponseWriter, args ...string) error {
	action, ok := registeredActions[args[0]]
	if !ok {
		return ErrNotFound
	}

	if len(args) == 2 && strings.TrimSpace(args[1]) == helpCommand {
		resp(action.Help())
		return nil
	}

	// drop the action name
	if len(args) > 0 {
		args = args[1:]
	}

	return action.Action(resp, args...)
}
