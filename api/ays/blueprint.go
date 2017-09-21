package ays

import (
	"encoding/json"
	"fmt"
	"net/http"
	"sync"
	"time"

	client "github.com/zero-os/0-orchestrator/api/ays/ays-client"
	"github.com/zero-os/0-orchestrator/api/httperror"
	yaml "gopkg.in/yaml.v2"

	log "github.com/Sirupsen/logrus"
)

func BlueprintName(role, name, action string) string {
	return fmt.Sprintf("%s_%s_%s_%+v", role, name, action, time.Now().Unix())
}

// Blueprint represent the content of a blueprint, which is a yaml file
type Blueprint map[string]interface{}

// ActionBlock
type ActionBlock struct {
	Action  string `json:"action"`
	Actor   string `json:"actor"`
	Service string `json:"service"`
	Force   bool   `json:"force" validate:"omitempty"`
}

// CreateBlueprint create a blueprint called name
func (c *Client) CreateBlueprint(name string, blueprint Blueprint) *Error {
	bpYaml, err := yaml.Marshal(blueprint)

	bp := client.Blueprint{
		Content: string(bpYaml),
		Name:    name,
	}

	_, resp, err := c.AYS().CreateBlueprint(c.repo, bp, nil, nil)
	if err != nil {
		return newError(resp, err)
	}

	if resp.StatusCode != http.StatusCreated && resp.StatusCode != http.StatusConflict {
		return newError(resp, fmt.Errorf(resp.Status))
	}

	return nil
}

// DeleteBlueprint delete the blueprint called name
// if no blueprint exists with this name, error is nil
func (c *Client) DeleteBlueprint(name string) error {
	resp, err := c.AYS().DeleteBlueprint(name, c.repo, nil, nil)
	if err != nil {
		return newError(resp, err)
	}

	if resp.StatusCode != http.StatusNoContent {
		return newError(resp, fmt.Errorf(resp.Status))
	}

	return nil
}

// ArchiveBlueprint archives the blueprint called name
// if no blueprint exists with this name, error is nil
func (c *Client) ArchiveBlueprint(name string) error {
	resp, err := c.AYS().ArchiveBlueprint(name, c.repo, nil, nil)
	if err != nil {
		return newError(resp, err)
	}
	if resp.StatusCode != http.StatusOK {
		return newError(resp, fmt.Errorf(resp.Status))
	}

	return nil
}

// ProcessChangeJobs represent a list of job id of a processChange job in AYS
// this is required sometime cause some execution of blueprint automaticly
// triggers process change job without a run execution.
type ProcessChangeJobs struct {
	client *Client
	JobIDs []string
}

// Wait blocks until all the jobs are done
func (p *ProcessChangeJobs) Wait() error {
	wg := sync.WaitGroup{}
	errs := make([]error, len(p.JobIDs))

	wg.Add(len(p.JobIDs))
	for i, jobID := range p.JobIDs {
		go func(i int, jobID string) {
			defer wg.Done()
			errs[i] = p.waitJob(jobID)
		}(i, jobID)
	}

	wg.Wait()

	errMsg := ""
	for _, err := range errs {
		if err != nil {
			errMsg += fmt.Sprintf("\n%s", err.Error())
			log.Errorf("error waiting for job: %v", err)
		}
	}
	if errMsg == "" {
		return nil
	}

	return fmt.Errorf("error waiting for jobs: %s", errMsg)
}

func (p *ProcessChangeJobs) waitJob(jobID string) error {
	var (
		job  client.Job
		resp *http.Response
		err  error
	)

	// Get Job status
	job, resp, err = p.client.client.Ays.GetJob(jobID, p.client.repo, nil, nil)
	if err != nil || resp.StatusCode != http.StatusOK {
		return newError(resp, err)
	}

	// Block until the job is finshed
	for job.State == "new" || job.State == "running" {
		time.Sleep(time.Second)

		job, resp, err = p.client.client.Ays.GetJob(jobID, p.client.repo, nil, nil)
		if err != nil || resp.StatusCode != http.StatusOK {
			return newError(resp, err)
		}
	}

	if job.Result != "" {
		aysErr := aysError{}
		// extract error from the job
		if err := json.Unmarshal([]byte(job.Result), &aysErr); err != nil {
			return err
		}
		return fmt.Errorf(aysErr.Message)
	}

	return nil
}

// ExecuteBlueprint executes the blueprint called name
// if no blueprint exists with this name, error is nil
func (c *Client) ExecuteBlueprint(name string) (*ProcessChangeJobs, error) {
	errBody := struct {
		Error string `json:"error"`
	}{}
	respData := struct {
		Msg               string   `json:"msg"`
		ProcessChangeJobs []string `json:"processChangeJobs"`
	}{}

	resp, err := c.AYS().ExecuteBlueprint(name, c.repo, nil, nil)
	if err != nil {
		return nil, newError(resp, err)
	}

	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		if err := json.NewDecoder(resp.Body).Decode(&errBody); err != nil {
			return nil, newError(resp, fmt.Errorf("Error decoding response body"))
		}
		return nil, httperror.New(resp, errBody.Error)
	}

	if err := json.NewDecoder(resp.Body).Decode(&respData); err != nil {
		return nil, newError(resp, fmt.Errorf("Error decoding response body"))
	}

	return &ProcessChangeJobs{
		JobIDs: respData.ProcessChangeJobs,
		client: c,
	}, nil
}
