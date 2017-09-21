package callback

// import (
// 	"bytes"
// 	"context"
// 	"encoding/json"
// 	"fmt"
// 	"net/http"
// 	"net/http/httptest"
// 	"sync"
// 	"testing"

// 	log "github.com/Sirupsen/logrus"
// 	"github.com/stretchr/testify/assert"
// 	"github.com/stretchr/testify/require"
// )

// func TestCallBack(t *testing.T) {
// 	log.SetLevel(log.DebugLevel)
// 	ctx, cancel := context.WithCancel(context.Background())
// 	defer cancel()
// 	cbRountine := newCallbackRoutine(ctx, "localhost:8080")

// 	runid := "testrunid"
// 	cbChan, cbURL := cbRountine.register(runid)
// 	assert.Equal(t, cbURL, "http://localhost:8080/callback?uuid=testrunid")

// 	wg := sync.WaitGroup{}

// 	wait := func(cbChan <-chan CallbackStatus) {
// 		wg.Add(1)
// 		go func() {
// 			defer wg.Done()
// 			i := 0
// 			var status CallbackStatus
// 			for status = range cbChan {
// 				if status == CallbackStatusOk {
// 					break
// 				}
// 				i++
// 			}
// 			assert.Equal(t, CallbackStatusOk, status)
// 		}()
// 	}

// 	sendRequest := func(url string, state CallbackStatus) {
// 		reqBody := &bytes.Buffer{}
// 		payload := callbackPayload{
// 			RunID: "testrunid",
// 			State: state,
// 		}
// 		err := json.NewEncoder(reqBody).Encode(payload)
// 		require.NoError(t, err)

// 		req := httptest.NewRequest("POST", url, reqBody)
// 		w := httptest.NewRecorder()
// 		fmt.Printf("send request to %v\n", url)
// 		cbRountine.handler(w, req)

// 		resp := w.Result()
// 		assert.Equal(t, http.StatusOK, resp.StatusCode)
// 	}

// 	sendRequest(cbURL, "error")
// 	sendRequest(cbURL, "error")
// 	sendRequest(cbURL, "error")
// 	sendRequest(cbURL, "error")
// 	sendRequest(cbURL, "error")
// 	// sendRequest(cbURL, "error")
// 	// wait(cbChan)
// 	// sendRequest(cbURL, "ok")

// 	cbRountine.register("newuiid")
// 	cbRountine.register("newuiid2")
// 	cb, url := cbRountine.register("newuiid3")
// 	wait(cb)
// 	sendRequest(url, "ok")
// 	wait(cbChan)

// 	wg.Wait()
// }

// // func TestCallBackGlobal(t *testing.T) {
// // 	ctx, cancel := context.WithCancel(context.Background())
// // 	defer cancel()

// // 	mux := http.NewServeMux()
// // 	mux.HandleFunc("/callback", Handler())
// // 	srv := httptest.NewServer(mux)

// // 	Init(ctx, srv.URL)

// // 	cbChan, cbURL := Register()
// // }

// // type lockMap struct {
// // 	mmap map[interface{}]interface{}
// // 	mu   sync.Mutex
// // }

// // func NewLockMap() *lockMap {
// // 	return &lockMap{
// // 		mmap: make(map[interface{}]interface{}),
// // 		mu:   sync.Mutex{},
// // 	}
// // }

// // func (m *lockMap) Get(key interface{}) (interface{}, bool) {
// // 	m.mu.Lock()
// // 	defer m.mu.Unlock()
// // 	val, ok := m.mmap[key]
// // 	return val, ok
// // }

// // func (m *lockMap) Set(key, value interface{}) {
// // 	m.mu.Lock()
// // 	defer m.mu.Unlock()
// // 	m.mmap[key] = value
// // }

// // type Map interface {
// // 	Set(key, val interface{})
// // 	Get(key interface{}) (interface{}, bool)
// // }

// // func BenchmarkLockMap(b *testing.B) {

// // 	listMap := map[string]Map{
// // 		"lockmap": NewLockMap(),
// // 		"pmap":    pmap.NewParallelMap(),
// // 	}

// // 	for name, m := range listMap {
// // 		b.Run(name, func(b *testing.B) {
// // 			for i := 0; i < b.N; i++ {
// // 				benchMap(m)
// // 			}
// // 		})
// // 	}
// // }

// // func benchMap(m Map) {
// // 	for i := 0; i < 10000; i++ {
// // 		m.Set(i, i)
// // 	}

// // 	numCouroutine := 100
// // 	wg := sync.WaitGroup{}
// // 	wg.Add(numCouroutine)
// // 	for i := 0; i < numCouroutine; i++ {
// // 		go func() {
// // 			defer wg.Done()
// // 			for j := 0; j < 10000; j++ {
// // 				if val, ok := m.Get(i); ok {
// // 					_ = val
// // 				}
// // 			}
// // 		}()
// // 	}
// // 	wg.Wait()
// // }

// // // func BenchmarkPMap(b *testing.B) {

// // // 	// wg := sync.WaitGroup{}
// // // 	// numCouroutine := 10
// // // 	m := pmap.NewParallelMap()

// // // 	for i := 0; i < b.N; i++ {
// // // 		m.Set(i, i)
// // // 		if val, ok := m.Get(i); ok {
// // // 			_ = val
// // // 		}
// // // 	}
// // // 	// wg.Add(numCouroutine)
// // // 	// for i := 0; i < numCouroutine; i++ {
// // // 	// 	go func() {

// // // 	// 	}()
// // // 	// }
// // // }
