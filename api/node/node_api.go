package node

import ays "github.com/g8os/grid/api/ays-client"

// NodeAPI is API implementation of /node root endpoint
type NodeAPI struct {
	AysRepo string
	AysAPI  *ays.AtYourServiceAPI
}

func NewNodeAPI(repo string, client *ays.AtYourServiceAPI) NodeAPI {
	return NodeAPI{
		AysRepo: repo,
		AysAPI:  client,
	}
}
