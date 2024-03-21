package resources

import (
	"strings"

	"github.com/gitdatcode/resources/internal/models/commands"
)

func init() {
	resources := Resources{}

	commands.Register(resources)
}

type Element struct {
	Type  string `json:"type"`
	Label string `json:"label"`
	Name  string `json:"name"`
	Value any    `json:"value"`
	Hint  string `json:"hint"`
}

type ResourceForm struct {
	Title       string    `json:"title"`
	SubmitLabel string    `json:"submit_label"`
	CallbackID  string    `json:"callback_id"`
	Elements    []Element `json:"elements"`
}

type Resource struct {
	Title string `json:"title"`
	URL   string `json:"url"`
}

type Resources struct {
}

func (r Resources) Name() string {
	return "resources"
}

func (r Resources) Help() string {
	return `Manages DATCODE resources

/resources (without any arguments) -- will show a form to create a new resource

/resources help -- will display this help text

/resources some search #string @user -- will parse the search string and return results
`
}

func (r Resources) Command(resp commands.ResponseWriter, args ...string) error {
	switch len(args) {
	case 0:
		r.newResourceForm(resp)

	default:
		searchString := strings.Join(args[1:], " ")
		r.resourceSearch(resp, searchString)
	}

	return nil
}

func (r Resources) newResourceForm(resp commands.ResponseWriter) {
	r.editResourceForm(resp, "new", "", "", "", "")
}

func (r Resources) editResourceForm(resp commands.ResponseWriter, callbackID, title, uri, tags, description string) {
	callbackID = "manage_resource::" + callbackID
	form := ResourceForm{
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
	}

	resp(form)
}

func (r Resources) resourceSearch(resp commands.ResponseWriter, searchString string) {

}
