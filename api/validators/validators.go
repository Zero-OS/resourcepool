package validators

import (
	"errors"
	"fmt"
	"gopkg.in/validator.v2"
	"reflect"
	"regexp"
)

func init() {
	validator.SetValidationFunc("cidr", cidr)
	validator.SetValidationFunc("ip", ip)
	validator.SetValidationFunc("macaddress", macAddress)
	validator.SetValidationFunc("servicename", serviceName)
}

// Validates that a string is a valid ays service name
func serviceName(v interface{}, param string) error {
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

// Validates that a string is a valid ip
func ip(v interface{}, param string) error {
	ip := reflect.ValueOf(v)
	if ip.Kind() != reflect.String {
		return errors.New("ip only validates strings")
	}

	ipValue := ip.String()
	if param == "empty" && ipValue == "" {
		return nil
	}

	re, _ := regexp.Compile(`^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$`)
	match := re.FindString(ipValue)

	if match == "" {
		return errors.New("string is not a valid ip address.")
	}

	return nil
}

// Validates that a string is a valid ip
func cidr(v interface{}, param string) error {
	cidr := reflect.ValueOf(v)
	if cidr.Kind() != reflect.String {
		return errors.New("cidr only validates strings")
	}

	cidrValue := cidr.String()
	if param == "empty" && cidrValue == "" {
		return nil
	}

	re, _ := regexp.Compile(`^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(/([0-9]|[1-2][0-9]|3[0-2]))$`)
	match := re.FindString(cidrValue)

	if match == "" {
		return errors.New("string is not a valid cidr.")
	}

	return nil
}

// Validates that a string is a valid macAddress
func macAddress(v interface{}, param string) error {
	addr := reflect.ValueOf(v)
	if addr.Kind() != reflect.String {
		return errors.New("macAddress only validates strings")
	}

	addrValue := addr.String()
	if param == "empty" && addrValue == "" {
		return nil
	}

	re, _ := regexp.Compile(`^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$`)
	match := re.FindString(addrValue)

	if match == "" {
		return errors.New("string is not a valid mac address.")
	}

	return nil
}

func ValidateEnum(fieldName string, value interface{}, enums map[interface{}]struct{}) error {
	if _, ok := enums[value]; ok {
		return nil
	}

	return fmt.Errorf("%v: %v is not a valid value.", fieldName, value)
}
