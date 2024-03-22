package cmd

import (
	"bytes"
	"database/sql"
	"encoding/json"
	"log"

	"github.com/emehrkay/pyt"
	_ "github.com/mattn/go-sqlite3"
	"github.com/spf13/cobra"

	"github.com/gitdatcode/resources/internal/env"
	"github.com/gitdatcode/resources/internal/service"

	// pull in any work registrations
	reg "github.com/gitdatcode/resources/work/resources"
)

var (
	serviceLayer *service.Resources
	slackToken   string
)

func init() {
	var err error

	slackToken = env.Get("SLACK_TOKEN", "")
	path := env.Get("DB_LOCATION", "./resources.db")
	path = "file:" + path + "?_foreign_keys=true"
	db, err := sql.Open("sqlite3", path)
	if err != nil {
		log.Fatalf(`unable to create sql @ %v -- %v`, path, err)
	}

	_, err = db.Exec(`
	pragma journal_mode = WAL;
	pragma synchronous = normal;
	pragma temp_store = memory;
	pragma mmap_size = 30000000000;
	`)
	if err != nil {
		log.Fatalf(`unable to set PRAGMA values -- %v`, err)
	}

	err = pyt.BuildSchema(db)
	if err != nil {
		log.Fatalf(`unable to create schema @ %v -- %v`, path, err)
	}

	serviceLayer, err = service.New(db)
	if err != nil {
		log.Fatalf(`unable to create service layer -- %v`, err)
	}

	reg.New(serviceLayer)
}

func jsonPrettyPrint(in []byte) string {
	var out bytes.Buffer
	err := json.Indent(&out, in, "", "\t")
	if err != nil {
		return string(in)
	}

	return out.String()
}

var RootCmd = &cobra.Command{
	Use:   "skills",
	Short: "",
}
