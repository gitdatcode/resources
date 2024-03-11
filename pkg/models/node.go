package models

import (
	"encoding/json"
	"strings"

	"github.com/gosimple/slug"

	"github.com/emehrkay/pyt"
)

const (
	NodeResource    string = "resource"
	NodeTag         string = "tag"
	NodeUser        string = "user"
	PrivateUserName string = "DATUser"
)

type ResourceSet pyt.NodeSet[Resource]

type Resource struct {
	Title       string `json:"title"`
	Uri         string `json:"uri"`
	Description string `json:"description"`
}

type ResourceSearchResultSet []ResourceSearchResult

type ResourceSearchResult struct {
	Tags     string          `json:"tags"`
	Resource pyt.GenericNode `json:"resource"`
	User     pyt.GenericNode `json:"user"`
}

func (r *ResourceSearchResult) GetTags() ([]Tag, error) {
	tags := []Tag{}

	for _, tagString := range strings.Split(r.Tags, "|||") {
		tag := Tag{}
		err := json.Unmarshal([]byte(tagString), &tag)
		if err != nil {
			return nil, err
		}

		tags = append(tags, tag)
	}

	return tags, nil
}

func (r *ResourceSearchResult) Scan() []any {
	return []any{
		&r.Tags,
		&r.Resource.ID,
		&r.Resource.Active,
		&r.Resource.Type,
		&r.Resource.Properties,
		&r.Resource.TimeCreated,
		&r.User.TimeUpdated,
		&r.User.ID,
		&r.User.Active,
		&r.User.Type,
		&r.User.Properties,
		&r.User.TimeCreated,
		&r.User.TimeUpdated,
	}
}

type TagSet pyt.NodeSet[Tag]

func (ts TagSet) IDs() []string {
	ids := make([]string, len(ts))

	for i, tag := range ts {
		ids[i] = tag.ID
	}

	return ids
}

func (ts TagSet) Tags() []Tag {
	tags := make([]Tag, len(ts))

	for i, tag := range ts {
		tags[i] = tag.Properties
	}

	return tags
}

func NewTag(tag string) *Tag {
	return &Tag{
		Tag:           tag,
		TagNormalized: slug.Make(tag),
	}
}

type Tag struct {
	Tag           string `json:"tag"`
	TagNormalized string `json:"tag_normalized"`
}

type UserSet pyt.NodeSet[User]

type User struct {
	Username string `json:"username"`
	SlackID  string `json:"slack_id"`
	Private  bool   `json:"private"`
}

func (u *User) GetPublicName() string {
	if u.Private {
		return PrivateUserName
	}

	return u.Username
}
