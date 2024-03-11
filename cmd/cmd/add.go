package cmd

import (
	"encoding/json"
	"fmt"
	"log"
	"strings"

	"github.com/gitdatcode/resources/pkg/models"
	"github.com/gitdatcode/resources/pkg/requests"
	"github.com/spf13/cobra"
)

func init() {
	var (
		title, description, uri, username, slackID, tags string
		private                                          bool
	)
	var add = &cobra.Command{
		Use:   "add",
		Short: "adds a new resource",
		Run: func(cmd *cobra.Command, args []string) {
			req := requests.CreateResource{
				Resource: models.Resource{
					Title:       title,
					Description: description,
					Uri:         uri,
				},
				User: models.User{
					Username: username,
					SlackID:  slackID,
					Private:  private,
				},
				Tags: strings.Split(tags, ","),
			}

			resp, err := serviceLayer.ResourceAdd(req)
			if err != nil {
				log.Fatalf(`unable to create new resource -- %v`, err)
			}

			resBytes, err := json.Marshal(resp)
			if err != nil {
				log.Fatalf(`unable to convert response to json -- %v`, err)
			}

			fmt.Println(jsonPrettyPrint(resBytes))
		},
	}

	add.PersistentFlags().StringVar(&title, "title", "", "a title for the resource")
	add.PersistentFlags().StringVar(&description, "description", "", "a description of the resource. This will be searched against")
	add.MarkPersistentFlagRequired("description")

	add.PersistentFlags().StringVar(&uri, "uri", "", "a uri of the resource")
	add.MarkPersistentFlagRequired("uri")

	add.PersistentFlags().StringVar(&username, "username", "", "the user who added the resource")
	add.MarkPersistentFlagRequired("username")

	add.PersistentFlags().StringVar(&slackID, "slack", "", "the slack id of the user")
	add.MarkPersistentFlagRequired("slack")

	add.PersistentFlags().StringVar(&tags, "tags", "", "a comma separated list of tags for the resource")
	add.MarkPersistentFlagRequired("tags")

	add.PersistentFlags().BoolVar(&private, "private", false, "flag stating if the user wants their name obscured")

	RootCmd.AddCommand(add)
}
