package node

import (
	"net/url"
	"strings"

	log "github.com/Sirupsen/logrus"
)

type FtpInfo struct {
	Host     string
	Username string
	Passwd   string
	Path     string
}

func GetFtpInfo(ftpUrl string) FtpInfo {
	var ftpinfo FtpInfo

	if !strings.HasPrefix(ftpUrl, "ftp://") {
		ftpUrl = "ftp://" + ftpUrl
	}

	parsedURL, err := url.Parse(ftpUrl)

	if err != nil {
		log.Error(err)
	}

	ftpinfo.Host = parsedURL.Host
	ftpinfo.Path = strings.Trim(parsedURL.Path, "/")
	if strings.Contains(ftpUrl, "@") {
		ftpinfo.Username = parsedURL.User.Username()
		passwd, isSet := parsedURL.User.Password()
		if isSet {
			ftpinfo.Passwd = passwd
		}
	}
	return ftpinfo
}
