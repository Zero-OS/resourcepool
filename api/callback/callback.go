package callback

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"sync"

	log "github.com/Sirupsen/logrus"
	"github.com/zero-os/0-orchestrator/api/httperror"
)

var (
	cbHandler CallbackHandler
)

type CallbackStatus int

const (
	// CallbackStatusOk is the value return when a runs executed succefully
	CallbackStatusOk CallbackStatus = iota
	// CallbackStatusFailure is the value return when a runs failed
	CallbackStatusFailure
)

type CallbackHandler interface {
	Handler(w http.ResponseWriter, r *http.Request)
	Wait(uid string) <-chan CallbackStatus
}

type waitRequest struct {
	uid    string
	cbChan chan CallbackStatus
}

type callBackRoutine struct {
	ctx context.Context
	// this channel receive the Wait requests
	cReq chan *waitRequest

	// this map a uid to a channel on which to send callback status
	callbackMap map[string]chan CallbackStatus
	mu          sync.RWMutex
}

func NewCallbackRoutine(ctx context.Context) CallbackHandler {
	cb := &callBackRoutine{
		ctx:         ctx,
		cReq:        make(chan *waitRequest),
		callbackMap: make(map[string]chan CallbackStatus),
		mu:          sync.RWMutex{},
	}
	cb.start()
	cbHandler = cb
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
			if _, ok := c.callbackMap[req.uid]; ok {
				log.Warning("erase callback for %s", req.uid)
			}
			c.callbackMap[req.uid] = req.cbChan
		}
	}()
}

type callbackPayload struct {
	RunID string `json:"runid"`
	State string `json:"runState"`
}

func (c *callBackRoutine) Handler(w http.ResponseWriter, r *http.Request) {
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

// Wait return a chanel on which the caller can wait to received the status of
// the callback identify by uid
func (c *callBackRoutine) Wait(uid string) <-chan CallbackStatus {
	cbChan := make(chan CallbackStatus)

	c.cReq <- &waitRequest{
		uid:    uid,
		cbChan: cbChan,
	}

	return cbChan
}
