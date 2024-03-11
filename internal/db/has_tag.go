package db

import (
	"database/sql"

	"github.com/emehrkay/pyt"
	"github.com/gitdatcode/resources/pkg/models"
	"github.com/google/uuid"
)

func (m *Manager) HasTagCreate(tx *sql.Tx, resourceID string, tagIDs ...string) (*models.HasTagSet, error) {
	hasTags := models.HasTagSet{}

	for _, tID := range tagIDs {
		h := pyt.NewEdge(uuid.NewString(), models.EdgeHasTag, resourceID, tID, models.HasTag{})
		hasTags = append(hasTags, *h)
	}

	newHTs, err := pyt.EdgesCreate(tx, hasTags...)

	return (*models.HasTagSet)(newHTs), err
}
