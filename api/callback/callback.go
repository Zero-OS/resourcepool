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
// callback to the proper channels created with Register
func Init(ctx context.Context, bindAddr string) {
	cbRountine = newCallbackRoutine(ctx, bindAddr)
}

// Register return a channel on which the caller can wait to received the status of the callback
// and the callback url
func Register() (<-chan CallbackStatus, string) {
	if cbRountine == nil {
		panic("no package level callackHandler, call Init first")
	}
	uuid := uuid.NewRandom()

	return cbRountine.register(fmt.Sprintf("%x", uuid))
}

// Handler is the http handler that needs to be registred in the http router to receive the callback
func Handler() http.HandlerFunc {
	return cbRountine.handler
}

type CallbackStatus string

const (
	// CallbackStatusOk is the value return when a runs executed succefully
	CallbackStatusOk CallbackStatus = "ok"
	// CallbackStatusFailure is the value return when a runs failed
	CallbackStatusFailure CallbackStatus = "error"
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
			log.Info("stop callback gorountine")
			return
		case req := <-c.cReq: //TODO: chek if we need a buffered channel
			c.mu.Lock()
			if _, ok := c.callbackMap[req.uuid]; ok {
				log.Warning("erase callback for %s", req.uuid)
			}
			c.callbackMap[req.uuid] = req.cbChan
			c.mu.Unlock()
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

	if err := r.ParseForm(); err != nil {
		httperror.WriteError(w, http.StatusInternalServerError, fmt.Errorf("fail to parse form for callback:%v", err), "error while parsing requests")
		return
	}
	uuid := r.Form.Get("uuid")
	if uuid == "" {
		err := fmt.Errorf("no uuid specified in the callback query")
		httperror.WriteError(w, http.StatusInternalServerError, err, err.Error())
		return
	}
	log.Debugf("look for callback channel uuid :%s", uuid)

	c.mu.RLock()
	defer c.mu.RUnlock()
	cbChan, ok := c.callbackMap[uuid]
	if !ok {
		log.Warningf("callback received for run id %v, but no callback handler registered for it", cbData.RunID)
		return
	}

	// remove used runid from the callback map
	delete(c.callbackMap, cbData.RunID)

	switch cbData.State {
	case "ok":
		cbChan <- CallbackStatusOk
	case "error":
		cbChan <- CallbackStatusFailure
	default:
		log.Errorf("receveid callback with unknown state: %v", cbData.State)
	}
	w.WriteHeader(http.StatusOK)
}

// register registers a callback and return a chanel on which the caller can wait to received the status of the callback identify by uid
// and the callback url
func (c *callBackRoutine) register(uuid string) (<-chan CallbackStatus, string) {
	cbChan := make(chan CallbackStatus)

	c.cReq <- &waitRequest{
		uuid:   uuid,
		cbChan: cbChan,
	}
	url := fmt.Sprintf("http://%s/callback?uuid=%s", c.bindAddr, uuid)
	log.Debugf("register callback for %s", url)
	// TODO: don't hardcode /callback
	return cbChan, url
}
