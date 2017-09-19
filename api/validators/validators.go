package validators

import (
	"errors"
	"fmt"
	"net"
	"reflect"
	"regexp"
	"strings"

	"gopkg.in/validator.v2"
)

var serviceRegex = regexp.MustCompile(`^[a-zA-Z0-9-._]+$`)

func init() {
	validator.SetValidationFunc("cidr", cidr)
	validator.SetValidationFunc("ip", ip)
	validator.SetValidationFunc("ipv4", ipv4)
	validator.SetValidationFunc("ipv6", ipv6)
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

// Validates that a string is a valid ipv4/ipv6
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

// Validates that a string is a valid ipv4
func ipv4(v interface{}, param string) error {
	ip := reflect.ValueOf(v)
	if ip.Kind() != reflect.String {
		return errors.New("ip only validates strings")
	}

	ipValue := ip.String()
	if param == "empty" && ipValue == "" {
		return nil
	}

	match := net.ParseIP(ipValue)
	if match.To4() == nil {
		return errors.New("string is not a valid ipv4 address.")
	}

	return nil
}

// Validates that a string is a valid ipv6
func ipv6(v interface{}, param string) error {
	ip := reflect.ValueOf(v)
	if ip.Kind() != reflect.String {
		return errors.New("ip only validates strings")
	}

	ipValue := ip.String()
	if param == "empty" && ipValue == "" {
		return nil
	}

	match := net.ParseIP(ipValue)
	if match.To16() == nil || match.To4() != nil {
		return errors.New("string is not a valid ipv6 address.")
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

func ValidateContainerFilesystem(fs string) error {
	parts := strings.Split(fs, ":")
	if len(parts) != 2 {
		return fmt.Errorf("Invalid Filesystems format")
	}
	return nil
}

func ValidateIpInRange(cidr string, ip string) error {
	_, subnet, err := net.ParseCIDR(cidr)
	if err != nil {
		return fmt.Errorf("%v: is not a valid cidr", cidr)
	}
	clientip := net.ParseIP(ip)
	if subnet.Contains(clientip) {
		return nil
	}
	return fmt.Errorf("%v: ip is not in valid range for cidr %v ", ip, cidr)
}

func ValidateVdisk(vtype string, tlog string, template string, size int, backup string) error {
	if template != "" {
		if vtype != "boot" {
			return fmt.Errorf("Vdisks of type %v do not have template support", vtype)
		}
	}

	if tlog != "" && (vtype == "cache" || vtype == "tmp") {
		return fmt.Errorf("Vdisks of type %v can't be redundant", vtype)
	}

	if backup != "" && tlog == "" {
		return fmt.Errorf("Tlog storage cluster is required for vdisk backup")
	}

	if size < 512 {
		return fmt.Errorf("Invalid Blocksize, Blocksize should be larger than 512")
	}

	if size&(size-1) == 0 {
		return fmt.Errorf("Invalid Blocksize, Blocksize should be a power of 2")
	}
	return nil
}

func ValidateCIDROverlap(cidr1, cidr2 string) (bool, error) {
	if cidr1 == "" || cidr2 == "" {
		return false, nil
	}

	_, subnet1, err := net.ParseCIDR(cidr1)
	if err != nil {
		return false, fmt.Errorf("%v: is not a valid cidr", cidr1)
	}

	_, subnet2, err := net.ParseCIDR(cidr2)
	if err != nil {
		return false, fmt.Errorf("%v: is not a valid cidr", cidr2)
	}

	if subnet1.Contains(subnet2.IP) || subnet2.Contains(subnet1.IP) {
		return true, nil
	}

	return false, nil
}

func ValidateCluster(ctype string, k int, m int, nrServers int, metaDisk string) error {
	if ctype == "object" {
		if k == 0 || m == 0 {
			return fmt.Errorf("K and M values required for object clusters")
		}
		if metaDisk == "" {
			return fmt.Errorf("MetaDriveType is required for object clusters")
		}
	}
	if (k + m) > nrServers {
		return fmt.Errorf("Number of servers should be greater than or equal to dataShards + parityShards")
	}
	return nil
}

// ValidateFtpURL Validate if ftp url format is supported
// localhost:22;
// ftp://1.2.3.4:200;
// ftp://user@127.0.0.1:200;
// ftp://user:pass@12.30.120.200:3000;
// ftp://user:pass@12.30.120.200:3000/root/dir
func ValidateFtpURL(url string) error {
	pattern := "^(ftp://(\\w+(:.*)?@)?)?((\\d{1,3}.\\d{1,3}.\\d{1,3}.\\d{1,3})|[a-z]+):\\d+(/\\w+)*$"

	matched, err := regexp.MatchString(pattern, url)
	if err != nil {
		return err
	}

	if matched != true {
		return fmt.Errorf("Invalid ftp url format")
	}
	return nil
}
