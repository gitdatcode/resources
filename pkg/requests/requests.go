package requests

import (
	"math"
	"net/url"
	"regexp"
	"strconv"
	"strings"

	"github.com/emehrkay/pyt"
	"github.com/gitdatcode/resources/pkg/errors"
	"github.com/gitdatcode/resources/pkg/models"
	"github.com/gitdatcode/resources/pkg/types"
)

type Pagination struct {
	Total  int `json:"total"`
	Limit  int `json:"limit"`
	Offset int `json:"offset"`
}

type CreateResource struct {
	Resource models.Resource `json:"resource"`
	User     models.User     `json:"user"`
	Tags     []string        `json:"tags"`
}

func (cr CreateResource) Validate() *errors.Validation {
	val := &errors.Validation{}

	if strings.TrimSpace(cr.Resource.Description) == "" {
		val.Add("resource.descripiton", errors.INVALID_FIELD)
	}

	if strings.TrimSpace(cr.Resource.Uri) == "" {
		val.Add("resource.uri", errors.INVALID_FIELD)
	}

	if len(cr.Tags) == 0 {
		val.Add("tags", errors.INVALID_FIELD_VALUES)
	}

	if strings.TrimSpace(cr.User.Username) == "" {
		val.Add("user.username", errors.INVALID_FIELD)
	}

	if val.HasErrors() {
		return val
	}

	return nil
}

var (
	tagREMatch  = regexp.MustCompile(`(\#[\w\d-]+)`)
	userREMatch = regexp.MustCompile(`(\@[\w\d-]+)`)
)

func PowerSet(original []string) [][]string {
	powerSetSize := int(math.Pow(2, float64(len(original))))
	result := make([][]string, 0, powerSetSize)

	var index int
	for index < powerSetSize {
		var subSet []string

		for j, elem := range original {
			if index&(1<<uint(j)) > 0 {
				subSet = append(subSet, elem)
			}
		}

		result = append(result, subSet)
		index++
	}

	return result
}

func NewSearchResourcesFromURL(urlIns *url.URL) (*SearchResources, error) {
	qry := urlIns.Query()
	query := qry.Get("query")
	powerSet := qry.Get("powerset_cap")
	powerSetCap, err := strconv.Atoi(powerSet)
	if err != nil {
		powerSetCap = 5
	}

	limit, err := strconv.Atoi(qry.Get("limit"))
	if err != nil {
		limit = 50
	}

	offset, err := strconv.Atoi(qry.Get("offset"))
	if err != nil {
		offset = 0
	}

	sr, err := NewSearchResources(query, powerSetCap)
	if err != nil {
		return nil, err
	}

	sr.Pagination.Limit = limit
	sr.Pagination.Offset = offset

	return sr, nil
}

func NewSearchResources(query string, powerSetCap int) (*SearchResources, error) {
	sr := &SearchResources{
		OriginalQuery: query,
		Tags:          []string{},
		Users:         []string{},
		SearchQueries: []string{},
	}

	tagMatches := tagREMatch.FindAllStringSubmatch(query, -1)
	for _, tm := range tagMatches {
		sr.Tags = append(sr.Tags, tm[1][1:])
	}

	userMatches := userREMatch.FindAllStringSubmatch(query, -1)
	for _, um := range userMatches {
		sr.Users = append(sr.Users, um[1][1:])
	}

	query = tagREMatch.ReplaceAllString(query, "")
	query = userREMatch.ReplaceAllString(query, "")
	query = strings.Join(strings.Fields(query), " ")

	if len(query) > 0 {
		words := strings.Split(query, " ")
		if powerSetCap >= len(words) {
			powerSetCap = len(words)
		}

		words = words[:powerSetCap]
		for _, ps := range PowerSet(words) {
			if len(ps) == 0 {
				continue
			}

			sr.SearchQueries = append(sr.SearchQueries, strings.Join(ps, " "))
		}

		sr.SearchQueries = append(sr.SearchQueries, query)
	}

	return sr, nil
}

type SearchResources struct {
	OriginalQuery string     `json:"original_query"`
	SearchQueries []string   `json:"search_queries"`
	Tags          []string   `json:"tags"`
	Users         []string   `json:"users"`
	Pagination    Pagination `json:"pagination"`
}

type ResourcesResponse struct {
	Resources     types.ResourceSet `json:"resources"`
	Pagination    Pagination        `json:"pagination"`
	ExecutionTime int64             `json:"execution_time_ms"`
}

func (rr *ResourcesResponse) FromResourceSearchResult(results models.ResourceSearchResultSet) error {
	for _, result := range results {
		resp := ResourceResponse{}
		err := resp.FromResourceSearchResult(result)
		if err != nil {
			return err
		}

		rr.Resources = append(rr.Resources, resp.Resource)
	}

	return nil
}

type ResourceResponse struct {
	Resource types.Resource `json:"resource"`
}

func (rr *ResourceResponse) FromResourceSearchResult(result models.ResourceSearchResult) error {
	var err error

	rr.Resource.Tags, err = result.GetTags()
	if err != nil {
		return err
	}

	resource, err := pyt.GenericNodeToType[models.Resource](result.Resource)
	if err != nil {
		return err
	}

	rr.Resource.Resource = resource.Properties
	rr.Resource.CreatedTime = result.Resource.TimeCreated.T
	user, err := pyt.GenericNodeToType[models.User](result.User)
	if err != nil {
		return err
	}

	rr.Resource.Username = user.Properties.GetPublicName()

	return nil
}
