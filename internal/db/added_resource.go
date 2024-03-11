package db

import (
	"database/sql"

	"github.com/emehrkay/pyt"
	"github.com/gitdatcode/resources/pkg/models"
	"github.com/google/uuid"
)

func (m *Manager) AddedResourceCreate(tx *sql.Tx, userID, resourceID string) (*pyt.Edge[models.AddedResource], error) {
	ar := pyt.NewEdge(uuid.NewString(), models.EdgeAddedResource, userID, resourceID, models.AddedResource{})

	return pyt.EdgeCreate(tx, *ar)
}
