package validators

import (
	"errors"
	"fmt"
	"net"
	"reflect"
	"regexp"

	"gopkg.in/validator.v2"
)

var serviceRegex = regexp.MustCompile(`^[a-zA-Z0-9-._]+$`)

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

	match := serviceRegex.FindString(name.String())

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

	match := net.ParseIP(ipValue)

	if match == nil {
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

	_, _, err := net.ParseCIDR(cidrValue)

	if err != nil {
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

	_, err := net.ParseMAC(addrValue)

	if err != nil {
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

// An extensiotn to omitempty validation, in which omitempty will work on conditional only if base condition is met.
func ValidateConditional(base1 interface{}, base2 interface{}, conditional interface{}, name string) error {
	if base1 != base2 && conditional == "" {
		return fmt.Errorf("%v: nil is not a valid value", name)
	}
	return nil
}
