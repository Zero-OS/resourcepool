// +build go1.9

package ays

import (
	"fmt"
	"net/http"

	client "github.com/zero-os/0-orchestrator/api/ays/ays-client"
)

// Run represents a Run in AYS. IT contains all the steps AYS will do
// to execute some actions on the services
type Run = client.AYSRun

// GetRun retreive a run from AYS server
func (c *Client) GetRun(runID string) (*Run, error) {
	run, resp, err := c.AYS().GetRun(runID, c.repo, nil, nil)
	if err != nil {
		return nil, newError(resp, err)
	}

	if resp.StatusCode != http.StatusOK {
		return nil, newError(resp, fmt.Errorf("get run return status %v", resp.Status))
	}

	return run, nil
}
