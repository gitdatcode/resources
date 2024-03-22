package commands

import (
	"encoding/json"
	"fmt"
	"net/http"
)

// SlashCommand contains information about a request of the slash command
type SlashCommand struct {
	Token               string `json:"token"`
	TeamID              string `json:"team_id"`
	TeamDomain          string `json:"team_domain"`
	EnterpriseID        string `json:"enterprise_id,omitempty"`
	EnterpriseName      string `json:"enterprise_name,omitempty"`
	IsEnterpriseInstall bool   `json:"is_enterprise_install"`
	ChannelID           string `json:"channel_id"`
	ChannelName         string `json:"channel_name"`
	UserID              string `json:"user_id"`
	UserName            string `json:"user_name"`
	Command             string `json:"command"`
	Text                string `json:"text"`
	ResponseURL         string `json:"response_url"`
	TriggerID           string `json:"trigger_id"`
	APIAppID            string `json:"api_app_id"`
}

// SlashCommandParse will parse the request of the slash command
func SlashCommandParse(r *http.Request) (s SlashCommand, err error) {
	if err = r.ParseForm(); err != nil {
		return s, err
	}

	s.Token = r.PostForm.Get("token")
	s.TeamID = r.PostForm.Get("team_id")
	s.TeamDomain = r.PostForm.Get("team_domain")
	s.EnterpriseID = r.PostForm.Get("enterprise_id")
	s.EnterpriseName = r.PostForm.Get("enterprise_name")
	s.IsEnterpriseInstall = r.PostForm.Get("is_enterprise_install") == "true"
	s.ChannelID = r.PostForm.Get("channel_id")
	s.ChannelName = r.PostForm.Get("channel_name")
	s.UserID = r.PostForm.Get("user_id")
	s.UserName = r.PostForm.Get("user_name")
	s.Command = r.PostForm.Get("command")
	s.Text = r.PostForm.Get("text")
	s.ResponseURL = r.PostForm.Get("response_url")
	s.TriggerID = r.PostForm.Get("trigger_id")
	s.APIAppID = r.PostForm.Get("api_app_id")

	return s, nil
}

// ValidateToken validates verificationTokens
func (s SlashCommand) ValidateToken(verificationTokens ...string) bool {
	for _, token := range verificationTokens {
		if s.Token == token {
			return true
		}
	}

	return false
}

type GenericReponse map[string]any

type DialogSubmission[T any] struct {
	Type       string `json:"type"`
	Submission T      `json:"submission"`
	CallBackID string `json:"callback_id"`
	State      string `json:"state"`
	Team       struct {
		ID     string `json:"id"`
		Domain string `json:"domain"`
	} `json:"team"`
	User struct {
		ID   string `json:"id"`
		Name string `json:"name"`
	} `json:"user"`
	Channel struct {
		ID   string `json:"id"`
		Name string `json:"name"`
	} `json:"channel"`
	ActionTs    string `json:"action_ts"`
	Token       string `json:"token"`
	ResponseUrl string `json:"response_url"`
}

func DialogSubmissionParse(r *http.Request) (*DialogSubmission[GenericReponse], error) {
	if err := r.ParseForm(); err != nil {
		return nil, err
	}

	ds := DialogSubmission[GenericReponse]{}
	err := json.Unmarshal([]byte(r.Form["payload"][0]), &ds)
	if err != nil {
		return nil, fmt.Errorf(`unable to unmarshal form response payload into DialogSubmission -- %w`, err)
	}

	return &ds, nil
}
