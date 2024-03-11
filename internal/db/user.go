package db

import (
	"database/sql"

	"github.com/emehrkay/pyt"
	"github.com/gitdatcode/resources/pkg/models"
	"github.com/google/uuid"
)

func (m *Manager) UserUpsert(tx *sql.Tx, user models.User) (*pyt.Node[models.User], error) {
	existing, err := m.UserGet(tx, user.Username)
	if err == nil {
		return existing, nil
	} else if err != sql.ErrNoRows {
		return nil, err
	}

	return m.UserCreate(tx, user)
}

func (m *Manager) UserGet(tx *sql.Tx, userName string) (*pyt.Node[models.User], error) {
	filters := pyt.FilterSet{
		pyt.NewFilter("properties->>'username'", userName),
	}

	return pyt.NodeGetBy[models.User](tx, filters)
}

func (m *Manager) UserCreate(tx *sql.Tx, user models.User) (*pyt.Node[models.User], error) {
	node := pyt.NewNode(uuid.NewString(), models.NodeUser, user)

	return pyt.NodeCreate(tx, *node)
}
