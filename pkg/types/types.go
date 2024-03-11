package types

import (
	"time"

	"github.com/gitdatcode/resources/pkg/models"
)

type ResourceSet []Resource

type Resource struct {
	Resource    models.Resource `json:"resource"`
	CreatedTime time.Time       `json:"created_time"`
	Username    string          `json:"username"`
	Tags        []models.Tag    `json:"tags"`
}
