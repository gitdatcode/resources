package models

import "github.com/emehrkay/pyt"

const (
	EdgeHasTag        string = "has_tag"
	EdgeAddedResource string = "added_resource"
)

type HasTagSet pyt.EdgeSet[HasTag]

type HasTag struct{}

type AddedResource struct{}
