package validators

import (
	"errors"
	"gopkg.in/validator.v2"
	"reflect"
	"regexp"
)

func init() {
	validator.SetValidationFunc("servicename", ServiceName)
}

// Validates that a string is a valid
func ServiceName(v interface{}, param string) error {
	name := reflect.ValueOf(v)
	if name.Kind() != reflect.String {
		return errors.New("servicename only validates strings")
	}

	re, _ := regexp.Compile(`^[a-zA-Z0-9-._]+$`)
	match := re.FindString(name.String())

	if match == "" {
		return errors.New("string can only contain alphanumeric characters, _, - and .")
	}

	return nil
}
