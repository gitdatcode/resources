package cmd

import (
	"encoding/json"
	"fmt"
	"log"

	"github.com/gitdatcode/resources/pkg/requests"
	"github.com/spf13/cobra"
)

func init() {
	var (
		query       string
		pretty      bool
		powerSetCap int
		limit       int
		offset      int
	)
	var search = &cobra.Command{
		Use:   "search",
		Short: "search resources",
		Run: func(cmd *cobra.Command, args []string) {
			req, err := requests.NewSearchResources(query, powerSetCap)
			if err != nil {
				log.Fatalf(`unable to create search -- %v`, err)
			}
			req.Pagination.Limit = limit
			req.Pagination.Offset = offset

			resp, err := serviceLayer.ResourceSearch(*req)
			if err != nil {
				log.Fatalf(`unable to execute search -- %v`, err)
			}

			resBytes, err := json.Marshal(resp)
			if err != nil {
				log.Fatalf(`unable to convert response to json -- %v`, err)
			}

			if pretty {
				fmt.Println(jsonPrettyPrint(resBytes))
			} else {
				fmt.Println(string(resBytes))
			}
		},
	}

	search.PersistentFlags().StringVar(&query, "query", "", "a search query in the format of `some search string @username @username2 #tag #tag2 more search")
	search.PersistentFlags().BoolVar(&pretty, "pretty", true, "format the output")
	search.PersistentFlags().IntVar(&powerSetCap, "powerset", 5, "creates a powerset from the first x words for fake full text searching")
	search.PersistentFlags().IntVar(&limit, "limit", 50, "the number of results to return")
	search.PersistentFlags().IntVar(&offset, "offset", 0, "offset used for pagination through results")

	RootCmd.AddCommand(search)
}
