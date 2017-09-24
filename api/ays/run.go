package ays

import (
	"fmt"
	"net/http"
	"time"

	log "github.com/Sirupsen/logrus"
	"github.com/pborman/uuid"
	"github.com/zero-os/0-orchestrator/api/ays/callback"
)

// CreateRun creates a run
// if simulate is false, the run is not started just after creation, else the run is started directly
// if wait is true, this call will block until the run send a succesfull callback, or all the tries are done. Implies simulate to false
func (c *Client) CreateRun(simulate bool, wait bool) (*Run, error) {
	var (
		queryParams = map[string]interface{}{}
		cb          *callback.Callback
	)

	if simulate {
		queryParams["simulate"] = "true"
	}

	if !simulate && wait {
		cb = c.cbMgr.Register(uuid.NewRandom().String())
		queryParams["callback_url"] = cb.URL
	}

	run, resp, err := c.AYS().CreateRun(c.repo, nil, queryParams)
	if err != nil {
		return nil, newError(resp, err)
	}

	if resp.StatusCode != http.StatusOK {
		return nil, newError(resp, fmt.Errorf("failed to create a run, wrong status: %s", resp.Status))
	}

	if !simulate && wait {
		_, err := cb.Wait(time.Hour)
		if err != nil {
			log.Errorf("error waiting callback: %v", err)
			return nil, err
		}
	}

	return c.GetRun(run.Key)
}

// ExecuteRun executes a run.
// If wait is true, this call will block until the run send a succesfull callback, or all the tries are done
func (c *Client) ExecuteRun(runID string, wait bool) (*Run, error) {
	var (
		queryParams = map[string]interface{}{}
		cb          *callback.Callback
	)

	if wait {
		cb = c.cbMgr.Register(uuid.NewRandom().String())
		queryParams["callback_url"] = cb.URL
	}

	_, resp, err := c.AYS().ExecuteRun(runID, c.repo, nil, queryParams)
	if err != nil {
		return nil, newError(resp, err)
	}

	if resp.StatusCode != http.StatusOK {
		return nil, newError(resp, err)
	}

	if wait {
		_, err := cb.Wait(time.Hour)
		if err != nil {
			log.Errorf("error waiting callback: %v", err)
			return nil, err
		}
	}

	return c.GetRun(runID)
}
