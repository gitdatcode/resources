package web

import (
	"fmt"
	"net/http"
	"strings"

	"github.com/gitdatcode/resources/internal/models/commands"
)

func (server *Server) doBotCommnad(w http.ResponseWriter, r *http.Request) {
	command := strings.Split(r.PathValue("command"), " ")
	var writer = func(content any) {
		server.RespondJson(content, http.StatusOK, w)
	}

	err := commands.Command(writer, command...)
	if err != nil {
		msg := fmt.Sprintf(`unable to execute command: %v`, command)
		server.HandleError(w, err, msg)
		return
	}
}

func (server *Server) doBotAction(w http.ResponseWriter, r *http.Request) {

	var writer = func(content any) {
		server.RespondJson(content, http.StatusOK, w)
	}

	var action []string
	err := commands.ExecuteAction(writer, action...)
	if err != nil {
		// msg := fmt.Sprintf(`unable to execute action`)
		server.HandleError(w, err, `unable to execute action`)
		return
	}
}
