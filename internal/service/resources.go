package service

import (
	"database/sql"
	"fmt"
	"time"

	"github.com/gitdatcode/resources/internal/db"
	"github.com/gitdatcode/resources/pkg/requests"
	"github.com/gitdatcode/resources/pkg/types"
)

func New(sqlDB *sql.DB) (*Resources, error) {
	manager := db.New(sqlDB)
	res := &Resources{
		DBManager: manager,
	}

	return res, nil
}

type Resources struct {
	DBManager *db.Manager
}

func (r *Resources) ResourceAdd(request requests.CreateResource) (*requests.ResourceResponse, error) {
	errs := request.Validate()
	if errs != nil {
		return nil, errs
	}

	tx, err := r.DBManager.Tx()
	if err != nil {
		return nil, fmt.Errorf(`unable to start transaction -- %w`, err)
	}

	defer tx.Commit()

	user, err := r.DBManager.UserUpsert(tx, request.User)
	if err != nil {
		tx.Rollback()
		return nil, fmt.Errorf(`unable to upsert user -- %w`, err)
	}

	resource, err := r.DBManager.ResourceAdd(tx, request.Resource)
	if err != nil {
		tx.Rollback()
		return nil, fmt.Errorf(`unable to add resource -- %w`, err)
	}

	tags, err := r.DBManager.TagsUpsertByTag(tx, request.Tags...)
	if err != nil {
		tx.Rollback()
		return nil, fmt.Errorf(`unable to create tags -- %w`, err)
	}

	_, err = r.DBManager.HasTagCreate(tx, resource.ID, tags.IDs()...)
	if err != nil {
		tx.Rollback()
		return nil, fmt.Errorf(`unable to connect tags to resource -- %w`, err)
	}

	_, err = r.DBManager.AddedResourceCreate(tx, user.ID, resource.ID)
	if err != nil {
		tx.Rollback()
		return nil, fmt.Errorf(`unable to connect user to resource -- %w`, err)
	}

	resp := requests.ResourceResponse{
		Resource: types.Resource{
			Resource:    resource.Properties,
			Username:    user.Properties.GetPublicName(),
			Tags:        tags.Tags(),
			CreatedTime: resource.TimeCreated.T,
		},
	}

	return &resp, nil
}

func (r *Resources) ResourceSearch(request requests.SearchResources) (*requests.ResourcesResponse, error) {
	tx, err := r.DBManager.Tx()
	if err != nil {
		return nil, fmt.Errorf(`unable to start transaction -- %w`, err)
	}

	start := time.Now()
	total, res, err := r.DBManager.ResourceSearch(tx, request.Pagination.Limit, request.Pagination.Offset, request.SearchQueries, request.Users, request.Tags)
	if err != nil {
		return nil, fmt.Errorf(`unable to search resources -- %w`, err)
	}

	resp := requests.ResourcesResponse{
		Pagination: request.Pagination,
	}
	resp.Pagination.Total = total
	err = resp.FromResourceSearchResult(*res)
	if err != nil {
		return nil, fmt.Errorf(`unable to create resp from search results -- %w`, err)
	}

	resp.ExecutionTime = time.Now().Sub(start).Milliseconds()

	return &resp, nil
}
