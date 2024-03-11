package db

import (
	"database/sql"

	"github.com/emehrkay/pyt"
	"github.com/gitdatcode/resources/pkg/models"
	"github.com/google/uuid"
)

func (m *Manager) TagsUpsertByTag(tx *sql.Tx, tags ...string) (*models.TagSet, error) {
	newTags := []models.Tag{}

	for _, tagName := range tags {
		nt := models.NewTag(tagName)
		newTags = append(newTags, *nt)
	}

	return m.TagsUpsert(tx, newTags...)
}

func (m *Manager) TagsUpsert(tx *sql.Tx, tags ...models.Tag) (*models.TagSet, error) {
	newTags := models.TagSet{}

	for _, t := range tags {
		tag, err := m.TagsGet(tx, t.Tag)
		if err == sql.ErrNoRows || tag == nil {
			tag, err := m.TagCreate(tx, t)
			if err != nil && err != sql.ErrNoRows {
				return nil, err
			}

			newTags = append(newTags, *tag)
			continue
		} else {
			newTags = append(newTags, *tag)
			continue
		}
	}

	return &newTags, nil
}

func (m *Manager) TagsGet(tx *sql.Tx, tagName string) (*pyt.Node[models.Tag], error) {
	filters := pyt.FilterSet{
		pyt.NewFilter("properties->>'tag'", tagName),
	}

	return pyt.NodeGetBy[models.Tag](tx, filters)
}

func (m *Manager) TagCreate(tx *sql.Tx, tag models.Tag) (*pyt.Node[models.Tag], error) {
	node := pyt.NewNode(uuid.NewString(), models.NodeTag, tag)

	return pyt.NodeCreate(tx, *node)
}
