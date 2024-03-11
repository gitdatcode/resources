package db

import "database/sql"

func New(sqlDB *sql.DB) *Manager {
	return &Manager{
		DB: sqlDB,
	}
}

type Manager struct {
	DB *sql.DB
}

func (m *Manager) Tx() (*sql.Tx, error) {
	return m.DB.Begin()
}
