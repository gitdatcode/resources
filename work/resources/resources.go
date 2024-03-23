package resources

import (
	"fmt"
	"strings"

	"github.com/gitdatcode/resources/internal/models/commands"
	"github.com/gitdatcode/resources/internal/service"
	"github.com/gitdatcode/resources/pkg/models"
	"github.com/gitdatcode/resources/pkg/requests"
	"github.com/gitdatcode/resources/pkg/types"
)

func New(serviceLayer *service.Resources) Resources {
	resources := Resources{
		serviceLayer: serviceLayer,
	}

	commands.Register(resources)

	return resources
}

type Element struct {
	Type  string `json:"type"`
	Label string `json:"label"`
	Name  string `json:"name"`
	Value any    `json:"value,omitempty"`
	Hint  string `json:"hint"`
}

type ResourceForm struct {
	Title       string    `json:"title"`
	SubmitLabel string    `json:"submit_label"`
	CallbackID  string    `json:"callback_id"`
	Elements    []Element `json:"elements"`
}

type Modal[T any] struct {
	TriggerID string `json:"trigger_id"`
	Dialog    T      `json:"dialog"`
}

type Resource struct {
	Title string `json:"title"`
	URL   string `json:"url"`
}

type Resources struct {
	serviceLayer *service.Resources
}

func (r Resources) Name() string {
	return "resource"
}

func (r Resources) Help() string {
	return `Manages DATCODE resources

/resources (without any arguments) -- will show a form to create a new resource

/resources help -- will display this help text

/resources some search #string @user -- will parse the search string and return results
`
}

func (r Resources) Command(resp commands.ResponseWriter, slashCommand commands.SlashCommand) error {
	if strings.TrimSpace(slashCommand.Text) == "" {
		r.newResourceForm(resp, slashCommand)
		return nil
	}

	r.resourceSearch(resp, slashCommand)

	return nil
}

func (r Resources) Action(resp commands.ResponseWriter, dialogSubmission commands.DialogSubmission[commands.GenericReponse]) error {
	tags := strings.Split(dialogSubmission.Submission["tags"].(string), ",")
	for i, t := range tags {
		tags[i] = strings.TrimSpace(t)
	}

	resResp, err := r.serviceLayer.ResourceAdd(requests.CreateResource{
		Resource: models.Resource{
			Uri:         dialogSubmission.Submission["url"].(string),
			Description: dialogSubmission.Submission["description"].(string),
		},
		User: models.User{
			Username: dialogSubmission.User.Name,
			SlackID:  dialogSubmission.User.ID,
		},
		Tags: tags,
	})
	if err != nil {
		return fmt.Errorf(`unable to add resource -- %w`, err)
	}

	searchRespFormated := ResourceSearchResponse{}
	searchRespFormated.FromResourceAdded(*resResp)
	commands.RespondJson(searchRespFormated, dialogSubmission.ResponseUrl)

	return nil
}

func (r Resources) newResourceForm(resp commands.ResponseWriter, slashCommand commands.SlashCommand) {
	r.editResourceForm(resp, slashCommand.TriggerID, "", "New Resource", "", "", "")
}

func (r Resources) editResourceForm(resp commands.ResponseWriter, triggerID, callbackID, title, uri, tags, description string) {
	callbackID = "resource/" + callbackID
	form := Modal[ResourceForm]{
		TriggerID: triggerID,
		Dialog: ResourceForm{
			Title:       title,
			CallbackID:  callbackID,
			SubmitLabel: "Save",
			Elements: []Element{
				{
					Type:  "text",
					Label: "URL",
					Name:  "url",
					Value: uri,
				},
				{
					Type:  "text",
					Label: "Tags",
					Name:  "tags",
					Value: tags,
					Hint:  "Comma,separated,tags,spaces are fine",
				},
				{
					Type:  "textarea",
					Label: "Description",
					Name:  "description",
					Value: description,
					Hint:  "Add a useful synopsis of the resource. It will be searhable with this content.",
				},
			},
		},
	}

	resp(form)
}

func (r Resources) resourceSearch(resp commands.ResponseWriter, slashCommand commands.SlashCommand) {
	req, err := requests.NewSearchResources(slashCommand.Text, 5)
	if err != nil {
		fmt.Println(err)
	}
	req.Pagination.Limit = 1000
	searchResp, err := r.serviceLayer.ResourceSearch(*req)
	if err != nil {
		fmt.Println(err, searchResp)
	}

	searchRespFormated := ResourceSearchResponse{}
	searchRespFormated.FromResourceSearch(slashCommand.Text, *searchResp)
	commands.RespondJson(searchRespFormated, slashCommand.ResponseURL)
}

type TextDef struct {
	Type  string `json:"type,omitempty"`
	Text  any    `json:"text,omitempty"`
	Emoji bool   `json:"emoji,omitempty"`
}

type Block struct {
	Type      string    `json:"type"`
	Text      *TextDef  `json:"text,omitempty"`
	Fields    []TextDef `json:"fields,omitempty"`
	Elements  []TextDef `json:"elements,omitempty"`
	Accessory *TextDef  `json:"accessory,omitempty"`
}

type ResourceSearchResponse struct {
	Blocks []Block `json:"blocks"`
}

func (r *ResourceSearchResponse) AddResource(res types.Resource) {
	tags := []TextDef{}
	for i, t := range res.Tags {
		if i > 24 {
			break
		}

		tags = append(tags, TextDef{
			Type: "button",
			Text: TextDef{
				Type: "plain_text",
				Text: t.Tag,
			},
		})
	}

	newMsgBlocks := []Block{
		{
			Type: "section",
			Fields: []TextDef{
				{
					Type: "mrkdwn",
					Text: res.Resource.Uri,
				},
			},
		},
		{
			Type: "section",
			Fields: []TextDef{
				{
					Type: "mrkdwn",
					Text: res.Resource.Description,
				},
			},
		},
		{
			Type:     "actions",
			Elements: tags,
		},
		{
			Type: "context",
			Elements: []TextDef{
				{
					Type: "mrkdwn",
					Text: res.CreatedTime.String(),
				},
				{
					Type: "mrkdwn",
					Text: res.Username,
				},
			},
		},
		{
			Type: "divider",
		},
	}

	// can only send 50 blocks in a response
	if len(r.Blocks)+len(newMsgBlocks) > 50 {
		return
	}

	r.Blocks = append(r.Blocks, newMsgBlocks...)
}

func (r *ResourceSearchResponse) FromResourceAdded(addResp requests.ResourceResponse) {
	r.Blocks = append(r.Blocks,
		Block{
			Type: "header",
			Text: &TextDef{
				Type: "plain_text",
				Text: `New Resource Added`,
			},
		})

	r.AddResource(addResp.Resource)
}

func (r *ResourceSearchResponse) FromResourceSearch(searchString string, searchResp requests.ResourcesResponse) {
	r.Blocks = append(r.Blocks,
		Block{
			Type: "header",
			Text: &TextDef{
				Type: "plain_text",
				Text: `Resources Search Results`,
			},
		},
		Block{
			Type: "context",
			Elements: []TextDef{
				{
					Type: "mrkdwn",
					Text: fmt.Sprintf("`%v` yielded `%d` results (not all returned)", searchString, len(searchResp.Resources)),
				},
			},
		})

	for _, res := range searchResp.Resources {
		r.AddResource(res)

		if len(r.Blocks) == 50 {
			break
		}
	}

	if len(r.Blocks) > 50 {
		r.Blocks = r.Blocks[:50]
	}
}
