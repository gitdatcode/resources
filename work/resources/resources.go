package resources

import (
	"fmt"
	"strings"

	"github.com/gitdatcode/resources/internal/models/commands"
	"github.com/gitdatcode/resources/internal/service"
	"github.com/gitdatcode/resources/pkg/models"
	"github.com/gitdatcode/resources/pkg/requests"
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

	r.resourceSearch(resp, slashCommand.Text)

	return nil
}

func (r Resources) Action(resp commands.ResponseWriter, dialogSubmission commands.DialogSubmission[commands.GenericReponse]) error {
	tags := strings.Split(dialogSubmission.Submission["tags"].(string), "")
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

	resp(resResp)
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

func (r Resources) resourceSearch(resp commands.ResponseWriter, searchString string) {

}
