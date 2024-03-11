package cmd

import (
	"database/sql"
	"encoding/csv"
	"log"
	"math"
	"os"
	"strconv"
	"strings"
	"time"

	"github.com/emehrkay/pyt"
	"github.com/spf13/cobra"

	"github.com/gitdatcode/resources/pkg/models"
)

func init() {
	var userMap = map[string]*pyt.Node[models.User]{}
	var resourceMap = map[string]*pyt.Node[models.Resource]{}
	var tagMap = map[string]*pyt.Node[models.Tag]{}
	var csvLocation string

	var updateTimes = func(tx *sql.Tx, recID string, created time.Time) {
		query := `
		UPDATE
			node
		SET
			time_created = ?
		WHERE
			id = ?
		`

		cr := pyt.Time{
			T: created,
		}
		crv, _ := cr.Value()
		_, err := tx.Exec(query, crv, recID)

		if err != nil {
			tx.Rollback()
			log.Fatalf(`unable to update times for record: %v -- %v`, recID, err)
		}
	}

	var loadCSV = func() {
		f, err := os.Open(csvLocation)
		if err != nil {
			log.Fatal(err)
		}

		defer f.Close()

		csvReader := csv.NewReader(f)
		data, err := csvReader.ReadAll()
		if err != nil {
			log.Fatal(err)
		}

		tx, err := serviceLayer.DBManager.Tx()
		if err != nil {
			log.Fatalf(`unable to create transacton -- %v`, err)
		}

		defer tx.Commit()

		// add the nodes
		for i, rec := range data {
			if i == 0 {
				continue
			}

			id := rec[0]
			if strings.TrimSpace(id) == "" {
				continue
			}

			nodeType := strings.ToLower(rec[1][1:])

			cre, err := strconv.ParseFloat(rec[4], 64)
			if err != nil {
				log.Fatalf(`unable to parse: %v as float -- %v`, rec[4], err)
			}
			sec, dec := math.Modf(cre)
			created := time.Unix(int64(sec), int64(dec*(1e9))).UTC()

			switch nodeType {
			case models.NodeResource:
				resource, err := serviceLayer.DBManager.ResourceAdd(tx, models.Resource{
					Title:       "",
					Description: rec[6],
					Uri:         rec[18],
				})
				if err != nil {
					tx.Rollback()
					log.Fatalf(`unable to create resource -- %v`, err)
				}

				resourceMap[id] = resource

				updateTimes(tx, resource.ID, created)

			case models.NodeTag:
				t := models.NewTag(rec[15])
				tag, err := serviceLayer.DBManager.TagCreate(tx, *t)
				if err != nil {
					tx.Rollback()
					log.Fatalf(`unable to create tag -- %v`, err)
				}

				tagMap[id] = tag

				updateTimes(tx, tag.ID, created)

			case models.NodeUser:
				var private bool
				if strings.ToLower(rec[20]) != "false" {
					private = true
				}

				user, err := serviceLayer.DBManager.UserCreate(tx, models.User{
					Username: rec[19],
					SlackID:  rec[14],
					Private:  private,
				})
				if err != nil {
					tx.Rollback()
					log.Fatalf(`unable to create user -- %v`, err)
				}

				userMap[id] = user

				updateTimes(tx, user.ID, created)

			}
		}

		// add the edges
		for _, rec := range data {
			eType := strings.ToLower(rec[23])
			inID := rec[21]
			outID := rec[22]

			switch eType {
			case "addedresource":
				user, ok := userMap[inID]
				if !ok {
					log.Fatalf(`no user with id: %v`, inID)
				}

				resource, ok := resourceMap[outID]
				if !ok {
					log.Fatalf(`no resource with id: %v`, outID)
				}

				_, err = serviceLayer.DBManager.AddedResourceCreate(tx, user.ID, resource.ID)
				if err != nil {
					tx.Rollback()
					log.Fatalf(`unable to connect user (%v) to resource (%v) -- %v`, user.ID, resource.ID, err)
				}

			case "hastag":
				resource, ok := resourceMap[inID]
				if !ok {
					log.Fatalf(`no resource with id: %v`, inID)
				}

				tag, ok := tagMap[outID]
				if !ok {
					log.Fatalf(`no tag with id: %v`, outID)
				}

				_, err = serviceLayer.DBManager.HasTagCreate(tx, resource.ID, tag.ID)
				if err != nil {
					tx.Rollback()
					log.Fatalf(`unable to connect resource (%v) to tag (%v) -- %v`, resource.ID, tag.ID, err)
				}
			}
		}
	}

	var load = &cobra.Command{
		Use:   "load",
		Short: "parses a neo4j csv backup of resources into the sqlite db which is located at envvar DB_LOCATION",
		Run: func(cmd *cobra.Command, args []string) {
			loadCSV()
		},
	}

	load.PersistentFlags().StringVar(&csvLocation, "csv", "./resources.csv", "the path to the neo4j csv dump")

	RootCmd.AddCommand(load)
}
