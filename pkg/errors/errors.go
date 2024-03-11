package errors

import (
	"fmt"
	"strings"
)

const (
	INVALID_FIELD        string = "invalid field"
	INVALID_FIELD_VALUES string = "invalid field values"
)

type Validation struct {
	errors map[string][]string
}

func (v *Validation) Add(key, error string) {
	if _, ok := v.errors[key]; !ok {
		v.errors[key] = []string{}
	}

	v.errors[key] = append(v.errors[key], error)
}

func (v *Validation) Error() string {
	errs := []string{}

	for e, v := range v.errors {
		if len(v) == 0 {
			continue
		}

		err := fmt.Sprintf(`%s: [%s]`, e, strings.Join(v, ", "))
		errs = append(errs, err)
	}

	return strings.Join(errs, " | ")
}

func (v *Validation) HasErrors() bool {
	return len(v.errors) > 0
}
