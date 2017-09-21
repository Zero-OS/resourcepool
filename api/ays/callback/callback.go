package callback

import (
	"encoding/json"
	"fmt"
	"net/http"
	"time"

	log "github.com/Sirupsen/logrus"
	cmap "github.com/orcaman/concurrent-map"
	"github.com/zero-os/0-orchestrator/api/httperror"
)

// var (
// 	cbRountine *callBackRoutine
// )

// Init start a go rountine that will wait for callback and distributed the
// callback to the proper channels created with Register
// func Init(bindAddr string) {
// 	cbRountine = newCallbackRoutine(bindAddr)
// }

// Register return a channel on which the caller can wait to received the status of the callback
// and the callback url
// func Register() string {
// 	if cbRountine == nil {
// 		panic("no package level callackHandler, call Init first")
// 	}
// 	uuid := uuid.NewRandom()

// 	return cbRountine.register(fmt.Sprintf("%x", uuid))
// }

// func Get(uuid string) (<-chan Status, error) {
// 	return cbRountine.get(uuid)
// }

// Handler is the http handler that needs to be registred in the http router to receive the callback
// func Handler() http.HandlerFunc {
// 	return cbRountine.handler
// }

// Status is the status of recevied from a callback
type Status string

const (
	// StatusOk is the value return when a runs executed succefully
	StatusOk Status = "ok"
	// StatusFailure is the value return when a runs failed
	StatusFailure Status = "error"
	// StatusTimeout is the value return when we reach a timeout waiting for a callback
	StatusTimeout Status = "timeout"
)

// type waitRequest struct {
// 	uuid   string
// 	cbChan chan CallbackStatus
// }

type Mgr struct {
	addr string
	// this map a uuid to a channel on which to send callback status
	cbMap cmap.ConcurrentMap
}

// NewMgr creates a new CallbackMgr, addr is the callback URL
func NewMgr(addr string) *Mgr {
	cb := &Mgr{
		addr:  addr,
		cbMap: cmap.New(),
	}

	// cbRountine = cb
	return cb
}

type callbackPayload struct {
	RunID string `json:"runid"`
	State Status `json:"runState"`
}

func (c *Mgr) handler(w http.ResponseWriter, r *http.Request) {
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

	if cbData.State != StatusOk && cbData.State != StatusFailure {
		log.Warning("recevie callback with unsported state: %v", cbData.State)
		return
	}

	log.Debugf("look for callback channel uuid: %s", uuid)
	var cbChan chan Status
	if tmp, ok := c.cbMap.Get(uuid); ok {
		cbChan = tmp.(chan Status)
	} else {
		log.Warningf("callback received for run id %v, but no callback handler registered for it", cbData.RunID)
		return
	}

	select {
	case cbChan <- cbData.State:
		log.Debugf("callback found for uuid: %v", uuid)
	default:
		log.Warning("callback chanel is full, closing chanel")
		// remove used runid from the callback map
		close(cbChan)
		c.cbMap.Remove(uuid)
	}

	w.WriteHeader(http.StatusOK)
}

// Callback is the object returned by Register, it allows you to wait for the end of a run
// and retreive its status
type Callback struct {
	UUID   string
	URL    string
	cbChan <-chan Status
}

// Wait waits till a run is done. It returns the status of the run and an error is the run took more time
// then timeout to finish
func (c *Callback) Wait(timeout time.Duration) (Status, error) {
	i := 0
	cTimeout := time.After(timeout)
	for {
		select {
		case status := <-c.cbChan:
			if status == StatusOk {
				return status, nil
			}
			i++
			if i >= 6 {
				return status, nil
			}
		case <-cTimeout:
			return Status(""), fmt.Errorf("timeout during wait of callback %s", c.UUID)
		}
	}
}

// Register registers a callback and return a chanel on which the caller can wait to received the status of the callback identify by uuid
// and the callback url
func (c *Mgr) Register(uuid string) *Callback {
	// size of 7 cause AYS can send up to 6 callback
	// so we have one extra room to not block on send
	cbChan := make(chan Status, 7)

	if has := c.cbMap.Has(uuid); has {
		log.Warning("erase callback for %s", uuid)
	}
	c.cbMap.Set(uuid, cbChan)

	url := fmt.Sprintf("%s?uuid=%s", c.addr, uuid)
	log.Debugf("register callback for %s", url)

	return &Callback{
		UUID:   uuid,
		cbChan: cbChan,
		URL:    url,
	}
}

// ErrCBChanelNotFound is returned when trying to get a callback channel with an uuid that doesn't exists
// type ErrCBChanelNotFound struct {
// 	uuid string
// }

// // Error implemet Error interface
// func (e ErrCBChanelNotFound) Error() string {
// 	return fmt.Sprintf("no callback found for uuid %s", e.uuid)
// }

// get return the callback channel associated with uuid.
// if no callback has been registred with this uuis, return nil and ErrCBChanelNotFound
// func (c *CallbackMgr) get(uuid string) (<-chan Status, error) {
// 	// var cbChan chan Status
// 	if tmp, ok := c.cbMap.Get(uuid); ok {
// 		return tmp.(chan Status), nil
// 	}
// 	return nil, ErrCBChanelNotFound{uuid}
// }
