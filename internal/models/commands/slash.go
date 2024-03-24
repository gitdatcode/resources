package commands

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
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
	APPTOKENID          string `json:"-"`
}

func jsonPrettyPrint(in []byte) string {
	var out bytes.Buffer
	err := json.Indent(&out, in, "", "\t")
	if err != nil {
		return string(in)
	}

	return out.String()
}

func RespondJson(content any, url string, headers map[string]string) error {
	by, err := json.Marshal(content)
	if err != nil {
		return err
	}
	fmt.Println(">>>>>>>>\n\n\n", jsonPrettyPrint(by), "\n\n\n>>>>>>>>\n\n\n*")
	req, err := http.NewRequest(http.MethodPost, url, bytes.NewReader(by))
	if err != nil {
		fmt.Println(err)
	}
	req.Header.Set("Content-Type", "application/json")

	for k, v := range headers {
		req.Header.Set(k, v)
	}

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		fmt.Println(err)
	}

	defer resp.Body.Close()
	b, e := io.ReadAll(resp.Body)
	fmt.Println(string(b), e)
	return nil
}

func RespondChannelJson(content any, url string, auth string) error {
	headers := map[string]string{
		"Authorization": fmt.Sprintf(`Bearer %s`, auth),
	}

	return RespondJson(content, url, headers)
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
	Type      string `json:"type"`
	APIAppID  string `json:"api_app_id"`
	Container struct {
		Type        string `json:"type"`
		MessageTs   string `json:"message_ts"`
		ChannelID   string `json:"channel_id"`
		IsEphemeral bool   `json:"is_ephemeral"`
	} `json:"container"`
	TriggerID  string `json:"trigger_id"`
	EnterPrise bool   `json:"enterprise"`
	Submission T      `json:"submission"`
	CallBackID string `json:"callback_id"`
	State      any    `json:"state"`
	Team       struct {
		ID     string `json:"id"`
		Domain string `json:"domain"`
	} `json:"team"`
	User struct {
		ID       string `json:"id"`
		Name     string `json:"name"`
		Username string `json:"username"`
		TeamID   string `json:"team_id"`
	} `json:"user"`
	Channel struct {
		ID   string `json:"id"`
		Name string `json:"name"`
	} `json:"channel"`
	ActionTs    string `json:"action_ts"`
	Token       string `json:"token"`
	ResponseUrl string `json:"response_url"`
	Actions     []struct {
		ActionID string `json:"action_id"`
		BlockID  string `json:"block_id"`
		Value    string `json:"value"`
		Type     string `json:"type"`
		ActionTS string `json:"action_ts"`
		Text     struct {
			Type  string `json:"type"`
			Text  string `json:"text"`
			Emoji bool   `json:"emoji"`
		} `json:"text"`
	} `json:"actions"`
	APPTOKENID string `json:"-"`
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
