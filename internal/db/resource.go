package db

import (
	"database/sql"
	"fmt"
	"strings"

	"github.com/emehrkay/pyt"
	"github.com/google/uuid"

	"github.com/gitdatcode/resources/internal/env"
	"github.com/gitdatcode/resources/pkg/models"
)

func (m *Manager) ResourceAdd(tx *sql.Tx, resource models.Resource) (*pyt.Node[models.Resource], error) {
	node := pyt.NewNode(uuid.NewString(), models.NodeResource, resource)

	return pyt.NodeCreate(tx, *node)
}

func (m *Manager) ResourceSearch(tx *sql.Tx, limit, offset int, searchStrings, usernames, tags []string) (int, *models.ResourceSearchResultSet, error) {
	var err error
	var whereExtra, tagHaving string
	params := []any{}

	if len(searchStrings) > 0 {
		var searchClauses []string

		for _, search := range searchStrings {
			searchClauses = append(searchClauses, `resource.properties->>'description' LIKE ?`)
			params = append(params, "%"+search+"%")
		}

		whereExtra = fmt.Sprintf(" AND (%s)", strings.Join(searchClauses, " OR "))
	}

	if len(usernames) > 0 {
		var userClauses []string

		for _, un := range usernames {
			userClauses = append(userClauses, `user.properties->>'username' = ?`)
			params = append(params, un)
		}

		whereExtra = fmt.Sprintf(`%s AND (%s)`, whereExtra, strings.Join(userClauses, " OR "))
	}

	if len(tags) > 0 {
		var tagClauses []string

		for _, tag := range tags {
			tagClauses = append(tagClauses, `(tag.properties->>'tag' = ? OR tag.properties->>'tag_normalized' = ?)`)
			params = append(params, tag, tag)
		}

		tagHaving = fmt.Sprintf(`HAVING (%s)`, strings.Join(tagClauses, " OR "))
	}

	query := fmt.Sprintf(`
	SELECT
		IFNULL(GROUP_CONCAT(tag.properties, '|||'), '') tags,
		resource.*,
		user.*
	FROM
		node resource
	LEFT JOIN
		edge added_resource ON added_resource.out_id = resource.id
	LEFT JOIN
		node user ON user.id = added_resource.in_id
	LEFT JOIN
		edge has_tag ON has_tag.in_id = resource.id
	LEFT JOIN
		node tag ON tag.id = has_tag.out_id
	WHERE
		resource.type = 'resource'
	%s
	GROUP BY
		resource.id
	%s
	ORDER BY
		resource.time_created DESC
	LIMIT
		?
	OFFSET
		?`, whereExtra, tagHaving)
	queryParams := append(params, limit, offset)

	if env.Get("QUERY_DEBUG", "") != "" {
		fmt.Printf("\n\n******\nsearch query:\n%s\n\nparams:\n%+v", query, queryParams)
	}

	rows, err := tx.Query(query, queryParams...)
	if err != nil && err != sql.ErrNoRows {
		return 0, nil, err
	}

	defer rows.Close()

	res := models.ResourceSearchResultSet{}
	for rows.Next() {
		rec := models.ResourceSearchResult{}
		err := rows.Scan(rec.Scan()...)
		if err != nil {
			return 0, nil, err
		}

		res = append(res, rec)
	}

	var total int
	totalQuery := fmt.Sprintf(`
	SELECT
		count(resource.id) OVER() AS TotalRecords
	FROM
		node resource
	LEFT JOIN
		edge added_resource ON added_resource.out_id = resource.id
	LEFT JOIN
		node user ON user.id = added_resource.in_id
	LEFT JOIN
		edge has_tag ON has_tag.in_id = resource.id
	LEFT JOIN
		node tag ON tag.id = has_tag.out_id
	WHERE
		resource.type = 'resource'
	%s
	GROUP BY
		resource.id
	%s
	LIMIT 1`, whereExtra, tagHaving)

	if env.Get("QUERY_DEBUG", "") != "" {
		fmt.Printf("\n\n******\ntotal query:\n%s\n\nparams:\n%+v", totalQuery, params)
	}

	err = tx.QueryRow(totalQuery, params...).Scan(&total)
	if err != nil && err != sql.ErrNoRows {
		return 0, nil, err
	}

	return total, &res, nil
}
