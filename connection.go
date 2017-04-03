package main

import (
	"context"
	"fmt"
	"github.com/g8os/go-client"
	"github.com/garyburd/redigo/redis"
	"github.com/gorilla/mux"
	"github.com/patrickmn/go-cache"
	"net/http"
	"strconv"
	"sync"
	"time"
)

const (
	connectionPoolMiddlewareKey         = "github.com/g8os/grid+connection-pool"
	connectionPoolMiddlewareDefaultPort = 6379
)

type ConnectionOptions func(*connectionMiddleware)

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
			c, err := redis.Dial("tcp", address)
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

func (c *connectionMiddleware) getConnection(ip string) client.Client {
	c.m.Lock()
	defer c.m.Unlock()

	if pool, ok := c.pools.Get(ip); ok {
		return client.NewClientWithPool(pool.(*redis.Pool))
	}

	pool := c.createPool(fmt.Sprintf("%s:%d", ip, c.port), c.password)

	c.pools.Set(ip, pool, cache.DefaultExpiration)
	return client.NewClientWithPool(pool)
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

func GetConnection(r *http.Request) client.Client {
	p := r.Context().Value(connectionPoolMiddlewareKey)
	if p == nil {
		panic("middleware not injected")
	}

	vars := mux.Vars(r)
	id := vars["nodeid"]

	mw := p.(*connectionMiddleware)

	return mw.getConnection(id)
}

func GetContainerConnection(r *http.Request) (client.Client, error) {
	vars := mux.Vars(r)
	id, err := strconv.Atoi(vars["containerid"])

	if err != nil {
		return nil, err
	}

	cl := GetConnection(r)
	contMgr := client.Container(cl)
	container := contMgr.Client(id)

	return container, nil
}
