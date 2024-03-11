# DatResources

DATCODE's esource management system.

## Requirements

* Go 1.22.x
* Either a copy of the resources.csv or resources.db (sqlite file)

### Build the executable

While in the project directory, run

```
go build -o resources cmd/main.go
```

### Running the program

The resources executable is a CLI app that can spawn a webserver. 

#### Availabe CLI commands:

| Command  | | Input |
| -------- | - | - |
| `./resources load` | Loads the Neo4j csv backup to the db. This onlhy needs to be done if the db hasnt already been created | `--csv /path/to/backup.csv` |
| `./resources add` | Adds a new resource to the db | `--title "some title"` `--description "resource description"` -`-user` `--slack_id` `--uri` |
| `./resources search` | Executes a search against the db | `--query "some search query @user @user #tag"` |
| `./resources web` | Starts the webserver | `--port=":9999"` |

#### Webserver Routes

| Method | URI | Params | Description |
| - |  - |  - |  - | 
| `GET` | `/search` | `query=some query string (same as cli)` `limit` `offset` `powerset_cap=5 (the number of items to turn into a powerset in lue of full text searching)` | Does a search against the db |
| `POST` | `/resource` | `{"user": {"username": "mark", "slack_id": "XXXX"}, "resource": {"description": "test"}, "tags": ["one", "two", "three"]}` | Creates a new resource and will create a new user if necessary |

## TO-DO

- [ ] Add functionality to manage users directly
- [ ] Add full text searching and drop the powerset term like matching
