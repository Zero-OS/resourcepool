package node

// NodeAPI is API implementation of /node root endpoint
type NodeAPI struct {
	AysRepo string
}

func NewNodeAPI(repo string) NodeAPI {
	return NodeAPI{
		AysRepo: repo,
	}
}
