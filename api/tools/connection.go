package tools

import (
	"context"
	"crypto/tls"
	"fmt"
	"net"
	"net/http"
	"sync"
	"time"

	"encoding/json"

	"strings"

	"github.com/garyburd/redigo/redis"
	"github.com/gorilla/mux"
	"github.com/patrickmn/go-cache"
	"github.com/zero-os/0-core/client/go-client"
	ays "github.com/zero-os/0-orchestrator/api/ays-client"
)

const (
	connectionPoolMiddlewareKey         = "github.com/zero-os/0-orchestrator+connection-pool"
	connectionPoolMiddlewareDefaultPort = 6379
)

type ConnectionOptions func(*connectionMiddleware)

type NAPI interface {
	ContainerCache() *cache.Cache
	AysAPIClient() *ays.AtYourServiceAPI
	AysRepoName() string
}

type API interface {
	AysAPIClient() *ays.AtYourServiceAPI
	AysRepoName() string
}

type redisInfo struct {
	RedisAddr     string
	RedisPort     int
	RedisPassword string
}

type NodeInfo struct {
	token string
	id    string
}

func ConnectionPortOption(port int) ConnectionOptions {
	return func(c *connectionMiddleware) {
		c.port = port
	}
}

func ConnectionPasswordOption(password string) ConnectionOptions {
	return func(c *connectionMiddleware) {
		c.password = password
	}
}

type connectionMiddleware struct {
	handler  http.Handler
	pools    *cache.Cache
	m        sync.Mutex
	port     int
	password string
}

func (c *connectionMiddleware) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	ctx := context.WithValue(r.Context(), connectionPoolMiddlewareKey, c)
	r = r.WithContext(ctx)

	c.handler.ServeHTTP(w, r)
}

func (c *connectionMiddleware) createPool(address, password string) *redis.Pool {
	pool := &redis.Pool{
		MaxIdle:     5,
		IdleTimeout: 5 * time.Minute,
		Dial: func() (redis.Conn, error) {
			// the redis protocol should probably be made sett-able
			c, err := redis.Dial("tcp", address, redis.DialNetDial(func(network, address string) (net.Conn, error) {
				return tls.Dial(network, address, &tls.Config{
					InsecureSkipVerify: true,
				})
			}))

			if err != nil {
				return nil, err
			}

			if len(password) > 0 {
				if _, err := c.Do("AUTH", password); err != nil {
					c.Close()
					return nil, err
				}
			} else {
				// check with PING
				if _, err := c.Do("PING"); err != nil {
					c.Close()
					return nil, err
				}
			}
			return c, err
		},
		// custom connection test method
		TestOnBorrow: func(c redis.Conn, t time.Time) error {
			if _, err := c.Do("PING"); err != nil {
				return err
			}
			return nil
		},
	}

	return pool
}

func (c *connectionMiddleware) getConnection(id NodeInfo, api NAPI) (client.Client, error) {
	c.m.Lock()
	defer c.m.Unlock()

	nodeId := id.id
	token := id.token
	poolId := fmt.Sprintf("%s#%s", nodeId, token) // i used # as it cannot be part of the token while . and _ can be , so it can parsed later on

	if pool, ok := c.pools.Get(poolId); ok {
		c.pools.Set(poolId, pool, cache.DefaultExpiration)
		return client.NewClientWithPool(pool.(*redis.Pool)), nil
	}
	srv, res, err := api.AysAPIClient().Ays.GetServiceByName(nodeId, "node", api.AysRepoName(), nil, nil)

	if err != nil {
		return nil, err
	}

	if res.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("Error getting service %v", id)
	}

	var info redisInfo
	if err := json.Unmarshal(srv.Data, &info); err != nil {
		return nil, err
	}

	pool := c.createPool(fmt.Sprintf("%s:%d", info.RedisAddr, int(info.RedisPort)), token)
	c.pools.Set(poolId, pool, cache.DefaultExpiration)
	return client.NewClientWithPool(pool), nil
}

func (c *connectionMiddleware) deleteConnection(id string) {
	c.pools.Delete(id)
}

func (c *connectionMiddleware) onEvict(_ string, x interface{}) {
	x.(*redis.Pool).Close()
}

func ConnectionMiddleware(opt ...ConnectionOptions) func(h http.Handler) http.Handler {
	return func(h http.Handler) http.Handler {
		p := &connectionMiddleware{
			pools:   cache.New(5*time.Minute, 1*time.Minute),
			port:    connectionPoolMiddlewareDefaultPort,
			handler: h,
		}

		p.pools.OnEvicted(p.onEvict)
		for _, o := range opt {
			o(p)
		}

		return p
	}
}

func GetAysConnection(r *http.Request, api API) AYStool {
	aysAPI := api.AysAPIClient()
	aysAPI.AuthHeader = r.Header.Get("Authorization")
	return GetAYSClient(aysAPI)
}

func GetConnection(r *http.Request, api NAPI) (client.Client, error) {
	p := r.Context().Value(connectionPoolMiddlewareKey)
	if p == nil {
		panic("middleware not injected")
	}

	vars := mux.Vars(r)
	token := strings.Split(r.Header.Get("Authorization"), " ")[1]
	id := NodeInfo{token, vars["nodeid"]}

	mw := p.(*connectionMiddleware)
	mw.password = token
	return mw.getConnection(id, api)
}

func GetContainerConnection(r *http.Request, api NAPI) (client.Client, error) {
	nodeClient, err := GetConnection(r, api)
	if err != nil {
		return nil, err
	}

	id, err := GetContainerId(r, api, nodeClient, "")
	if err != nil {
		return nil, err
	}

	container := client.Container(nodeClient).Client(id)

	return container, nil
}

func getContainerWithTag(containers map[int16]client.ContainerResult, tag string) int {
	for containerID, container := range containers {
		for _, containertag := range container.Container.Arguments.Tags {
			if containertag == tag {
				return int(containerID)
			}
		}
	}
	return 0
}

func GetContainerId(r *http.Request, api NAPI, nodeClient client.Client, containername string) (int, error) {
	vars := mux.Vars(r)
	if containername == "" {
		containername = vars["containername"]
	}
	c := api.ContainerCache()
	id := 0

	if cachedID, ok := c.Get(containername); !ok {
		containermanager := client.Container(nodeClient)
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
	c.Set(containername, id, cache.DefaultExpiration)
	return id, nil
}

func DeleteContainerId(r *http.Request, api NAPI) {
	vars := mux.Vars(r)
	c := api.ContainerCache()
	c.Delete(vars["containername"])
}

func DeleteConnection(r *http.Request) {
	p := r.Context().Value(connectionPoolMiddlewareKey)
	if p == nil {
		panic("middleware not injected")
	}

	vars := mux.Vars(r)
	mw := p.(*connectionMiddleware)
	mw.deleteConnection(vars["nodeid"])
}
