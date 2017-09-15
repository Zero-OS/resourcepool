package callback

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"sync"

	log "github.com/Sirupsen/logrus"
	"github.com/pborman/uuid"
	"github.com/zero-os/0-orchestrator/api/httperror"
)

var (
	cbRountine *callBackRoutine
)

// Init start a go rountine that will wait for callback and distributed the
// callback to the proper channels created with Wait
func Init(ctx context.Context, bindAddr string) {
	cbRountine = newCallbackRoutine(ctx, bindAddr)
}

// Wait return a channel on which the caller can wait to received the status of the callback
// and the callback url
func Wait() (<-chan CallbackStatus, string) {
	if cbRountine == nil {
		panic("no package level callackHandler, call NewCallbackRoutine first")
	}
	uuid := uuid.NewRandom()

	return cbRountine.wait(string(uuid))
}

// Handler is the http handler that needs to be registred in the http router to receive the callback
func Handler() http.HandlerFunc {
	return cbRountine.handler
}

type CallbackStatus int

const (
	// CallbackStatusOk is the value return when a runs executed succefully
	CallbackStatusOk CallbackStatus = iota
	// CallbackStatusFailure is the value return when a runs failed
	CallbackStatusFailure
)

type waitRequest struct {
	uuid   string
	cbChan chan CallbackStatus
}

type callBackRoutine struct {
	ctx      context.Context
	bindAddr string
	// this channel receive the Wait requests
	cReq chan *waitRequest

	// this map a uid to a channel on which to send callback status
	callbackMap map[string]chan CallbackStatus
	mu          sync.RWMutex
}

func newCallbackRoutine(ctx context.Context, bindAddr string) *callBackRoutine {
	cb := &callBackRoutine{
		ctx:         ctx,
		bindAddr:    bindAddr,
		cReq:        make(chan *waitRequest),
		callbackMap: make(map[string]chan CallbackStatus),
		mu:          sync.RWMutex{},
	}
	cb.start()
	cbRountine = cb
	return cb
}

func (c *callBackRoutine) start() {
	go func() {
		select {
		case <-c.ctx.Done():
			fmt.Println("stop callback gorountine")
			log.Info("stop callback gorountine")
			return
		case req := <-c.cReq: //TODO: chek if we need a buffered channel
			if _, ok := c.callbackMap[req.uuid]; ok {
				log.Warning("erase callback for %s", req.uuid)
			}
			c.callbackMap[req.uuid] = req.cbChan
		}
	}()
}

type callbackPayload struct {
	RunID string `json:"runid"`
	State string `json:"runState"`
}

func (c *callBackRoutine) handler(w http.ResponseWriter, r *http.Request) {
	cbData := callbackPayload{}
	defer r.Body.Close()
	if err := json.NewDecoder(r.Body).Decode(&cbData); err != nil {
		httperror.WriteError(w, http.StatusBadRequest, fmt.Errorf("fail to unmarshal callback body: %v", err), "wrong format of callback payload")
		return
	}

	c.mu.RLock()
	defer c.mu.RUnlock()
	cbChan, ok := c.callbackMap[cbData.RunID]
	if !ok {
		log.Warningf("callback received for run id %v, but no callback handler registered for it", cbData.RunID)
		return
	}

	// remove used runid from the callback map
	delete(c.callbackMap, cbData.RunID)

	switch cbData.State {
	case "ok":
		cbChan <- CallbackStatusOk
		close(cbChan)
	case "error":
		cbChan <- CallbackStatusFailure
		close(cbChan)
	default:
		log.Errorf("receveid callback with unknown state: %v", cbData.State)
	}
	w.WriteHeader(http.StatusOK)
}

// Wait return a chanel on which the caller can wait to received the status of the callback identify by uid
// and the callback url
func (c *callBackRoutine) wait(uuid string) (<-chan CallbackStatus, string) {
	cbChan := make(chan CallbackStatus)

	c.cReq <- &waitRequest{
		uuid:   uuid,
		cbChan: cbChan,
	}
	// TODO: don't hardcode /callback
	return cbChan, fmt.Sprintf("http://%s/callback?uid=%s", c.bindAddr, uuid)
}
