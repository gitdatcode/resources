package web

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"

	"github.com/gitdatcode/resources/internal/models/commands"
)

var (
	SLACKAPIURL string = "https://slack.com/api/"
)

func (server *Server) doBotCommnad(w http.ResponseWriter, r *http.Request) {
	slashCommand, err := commands.SlashCommandParse(r)
	if err != nil {
		w.Write([]byte("error"))
		return
	}

	var writer = func(content any) {
		by, err := json.Marshal(content)
		if err != nil {
			fmt.Println(err)
		}

		fmt.Println(string(by))

		req, err := http.NewRequest(http.MethodPost, SLACKAPIURL+"dialog.open", bytes.NewReader(by))
		if err != nil {
			fmt.Println(err)
		}
		req.Header.Set("Content-Type", "application/json")
		req.Header.Set("Authorization", fmt.Sprintf("Bearer %s", server.slackToken))
		client := &http.Client{}
		resp, err := client.Do(req)
		if err != nil {
			fmt.Println(err)
		}

		defer resp.Body.Close()
		b, e := io.ReadAll(resp.Body)
		fmt.Println(string(b), e)
	}

	err = commands.Command(writer, slashCommand)
	if err != nil {
		msg := fmt.Sprintf(`unable to execute command: %v`, slashCommand.Command)
		server.HandleError(w, err, msg)
		return
	}
}

func (server *Server) doBotAction(w http.ResponseWriter, r *http.Request) {
	dialogSubmission, err := commands.DialogSubmissionParse(r)
	if err != nil {
		w.Write([]byte("error"))
		return
	}

	var writer = func(content any) {
		server.RespondJson(content, http.StatusOK, w)
	}

	err = commands.ExecuteAction(writer, *dialogSubmission)
	if err != nil {
		// msg := fmt.Sprintf(`unable to execute action`)
		server.HandleError(w, err, `unable to execute action`)
		return
	}
}
