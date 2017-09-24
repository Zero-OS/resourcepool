package ays

import (
	"encoding/json"
	"fmt"
	"net/http"
	"sync"
	"time"

	log "github.com/Sirupsen/logrus"
	"github.com/garyburd/redigo/redis"
	"github.com/gorilla/mux"
	"github.com/patrickmn/go-cache"
	goclient "github.com/zero-os/0-core/client/go-client"
)

const (
	connectionPoolMiddlewareDefaultPort = 6379
)

type connectionMgr struct {
	client *Client
	pools  *cache.Cache
	m      sync.Mutex
	port   int
	// password string
}

type connectionOptions func(*connectionMgr)

// newConnectionMgr creates a new connecion manager
// it's used to get direct connection to the nodes and container
func newConnectionMgr(client *Client, opt ...connectionOptions) *connectionMgr {
	p := &connectionMgr{
		client: client,
		pools:  cache.New(5*time.Minute, 1*time.Minute),
		port:   connectionPoolMiddlewareDefaultPort,
	}

	p.pools.OnEvicted(p.onEvict)
	for _, o := range opt {
		o(p)
	}

	return p
}

func (c *connectionMgr) onEvict(_ string, x interface{}) {
	x.(*redis.Pool).Close()
}

func (c *connectionMgr) getNodeConnection(nodeid string) (goclient.Client, error) {
	c.m.Lock()
	defer c.m.Unlock()

	log.Debugf("get connection for %s", nodeid)

	srv, err := c.client.GetService("node", nodeid, "", nil)
	if err != nil {
		log.Errorf("error get connection for %s", nodeid)
		return nil, err
	}

	poolID := nodeid
	if c.client.token != "" {
		poolID = fmt.Sprintf("%s#%s", nodeid, c.client.token) // i used # as it cannot be part of the token while . and _ can be , so it can parsed later on
	}

	if pool, ok := c.pools.Get(poolID); ok {
		log.Debugf("connection from cache for %s", nodeid)
		c.pools.Set(poolID, pool, cache.DefaultExpiration)
		return goclient.NewClientWithPool(pool.(*redis.Pool)), nil
	}

	var info struct {
		RedisAddr     string
		RedisPort     int
		RedisPassword string
	}
	if err := json.Unmarshal(srv.Data, &info); err != nil {
		return nil, err
	}

	poolAddr := fmt.Sprintf("%s:%d", info.RedisAddr, int(info.RedisPort))
	log.Debugf("new connection for %s - %s", nodeid, poolAddr)
	log.Debugf("token: %s", c.client.token)
	pool := goclient.NewPool(poolAddr, c.client.token)
	c.pools.Set(poolID, pool, cache.DefaultExpiration)
	return goclient.NewClientWithPool(pool), nil
}

func (c *connectionMgr) deleteConnection(id string) {
	c.pools.Delete(id)
}

func getContainerWithTag(containers map[int16]goclient.ContainerResult, tag string) int {
	for containerID, container := range containers {
		for _, containertag := range container.Container.Arguments.Tags {
			if containertag == tag {
				return int(containerID)
			}
		}
	}
	return 0
}

func (c *connectionMgr) GetContainerID(r *http.Request, containername string) (int, error) {
	if containername == "" {
		vars := mux.Vars(r)
		containername = vars["containername"]
	}

	id := 0
	nodeClient, err := c.client.GetNodeConnection(r)
	if err != nil {
		return id, err
	}

	if cachedID, ok := c.client.cache.Get(containername); !ok {
		containermanager := goclient.Container(nodeClient)
		containers, err := containermanager.List()
		if err != nil {
			return id, err
		}
		id = getContainerWithTag(containers, containername)
	} else {
		id = cachedID.(int)
	}

	if id == 0 {
		return id, fmt.Errorf("ContainerID is not known")
	}

	c.client.cache.Set(containername, id, cache.DefaultExpiration)
	return id, nil
}

// GetNodeConnection return a client for direct node access.
// It extract the node id from the URL of the requests
func (c *Client) GetNodeConnection(r *http.Request) (goclient.Client, error) {
	vars := mux.Vars(r)
	nodeid := vars["nodeid"]
	if nodeid == "" {
		return nil, fmt.Errorf("node id not found")
	}
	return c.connectionMgr.getNodeConnection(nodeid)
}

//GetContainerConnection returns a client for a direct access into a container
// container id is extracted from r
func (c *Client) GetContainerConnection(r *http.Request) (goclient.Client, error) {
	nodeClient, err := c.GetNodeConnection(r)
	if err != nil {
		return nil, err
	}

	id, err := c.GetContainerID(r, "")
	if err != nil {
		return nil, err
	}

	return goclient.Container(nodeClient).Client(id), nil
}

// GetContainerID returns the id of the container associated with name.
// It connects to the node that host the container to do so. The node id is exrtaced from URL in r
func (c *Client) GetContainerID(r *http.Request, name string) (int, error) {
	return c.connectionMgr.GetContainerID(r, name)
}

func (c *Client) DeleteConnection(r *http.Request) {
	vars := mux.Vars(r)
	c.connectionMgr.deleteConnection(vars["nodeid"])
}

// DeleteContainerId remove the container id from the connection cache
// containerid is extracted from r
func (c *Client) DeleteContainerId(r *http.Request) {
	vars := mux.Vars(r)
	c.cache.Delete(vars["containername"])
}
