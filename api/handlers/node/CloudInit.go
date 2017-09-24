package node

import (
	"fmt"

	"gopkg.in/validator.v2"
	"gopkg.in/yaml.v2"
)

type CloudInit struct {
	MetaData string `yaml:"metadata" json:"metadata" validate:"nonzero"`
	UserData string `yaml:"userdata" json:"userdata" validate:"nonzero"`
}

func (s CloudInit) Validate() error {
	data := make(map[interface{}]interface{})
	if err := yaml.Unmarshal([]byte(s.MetaData), data); err != nil {
		return fmt.Errorf("Invalid meta-data, could not parse YAML: %s %s", s.MetaData, err)
	}
	if err := yaml.Unmarshal([]byte(s.UserData), data); err != nil {
		return fmt.Errorf("Invalid user-data, could not parse YAML: %s %s", s.UserData, err)
	}
	return validator.Validate(s)
}
