package tools

import (
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"time"

	yaml "gopkg.in/yaml.v2"

	ays "github.com/zero-os/0-orchestrator/api/ays-client"
)

var (
	ayscl *ays.AtYourServiceAPI
)

type AYStool struct {
	Ays *ays.AysService
}

type AYSError struct {
	Code    int    `json:"code"`
	Message string `json:"message"`
	err     error
}

type ActionBlock struct {
	Action  string `json:"action"`
	Actor   string `json:"actor"`
	Service string `json:"service"`
	Force   bool   `json:"force" validate:"omitempty"`
}

func GetAYSClient(client *ays.AtYourServiceAPI) AYStool {
	return AYStool{
		Ays: client.Ays,
	}
}

//ExecuteBlueprint runs ays operations needed to run blueprints. This will BLOCK until blueprint job is complete.
// create blueprint
// execute blueprint
// execute run
// archive the blueprint
func (aystool AYStool) ExecuteBlueprint(repoName, role, name, action string, blueprint map[string]interface{}) (*ays.AYSRun, error) {
	blueprintName, err := aystool.UpdateBlueprint(repoName, role, name, action, blueprint)
	if err != nil {
		return nil, err
	}

	run, err := aystool.runRepo(repoName)
	if err != nil {
		aystool.archiveBlueprint(blueprintName, repoName)
		return nil, err
	}

	return run, nil
}

//Update blueprint is used to do the ays blueprint action , creating a blueprint jobs (usually in processChange) and then will BLOCK on them.
func (aystool AYStool) UpdateBlueprint(repoName, role, name, action string, blueprint map[string]interface{}) (string, error) {
	blueprintName := fmt.Sprintf("%s_%s_%s_%+v", role, name, action, time.Now().Unix())

	if err := aystool.createBlueprint(repoName, blueprintName, blueprint); err != nil {
		return "", err
	}

	_, jobs, err := aystool.executeBlueprint(blueprintName, repoName)
	if err != nil {

		aystool.archiveBlueprint(blueprintName, repoName)
		return "", err
	}
	if len(jobs) > 0 {
		for _, job := range jobs {
			_, err := aystool.WaitJobDone(job, repoName)
			if err != nil {
				aystool.archiveBlueprint(blueprintName, repoName)
				return "", err
			}
		}
		return blueprintName, aystool.archiveBlueprint(blueprintName, repoName)
	}
	return blueprintName, aystool.archiveBlueprint(blueprintName, repoName)

}

func (aystool AYStool) WaitRunDone(runid, repoName string) (*ays.AYSRun, error) {
	run, err := aystool.getRun(runid, repoName)

	if err != nil {
		return run, err
	}

	for run.State == "new" || run.State == "running" {
		time.Sleep(time.Second)

		run, err = aystool.getRun(run.Key, repoName)
		if err != nil {
			return run, err
		}
	}
	return run, nil
}

func (aystool AYStool) WaitJobDone(jobid, repoName string) (ays.Job, error) {
	job, resp, err := aystool.Ays.GetJob(jobid, repoName, nil, nil)
	if err != nil || resp.StatusCode != http.StatusOK {
		return job, err
	}

	for job.State == "new" || job.State == "running" {
		time.Sleep(time.Second)

		job, resp, err = aystool.Ays.GetJob(job.Key, repoName, nil, nil)
		if err != nil {
			return job, err
		}
	}

	if job.State == "error" {
		err := AYSError{}
		if err := json.Unmarshal([]byte(job.Result), &err); err != nil {
			return job, err
		}

		err.err = fmt.Errorf(err.Message)
		errResp := http.Response{
			StatusCode: err.Code,
		}
		httperror := HTTPError{
			Resp: &errResp,
			err:  err.err,
		}
		return job, httperror
	}
	return job, nil
}

// ServiceExists check if an atyourserivce exists
func (aystool AYStool) ServiceExists(serviceName string, instance string, repoName string) (bool, error) {
	_, res, err := aystool.Ays.GetServiceByName(instance, serviceName, repoName, nil, nil)
	if err != nil {
		return false, err
	} else if res.StatusCode == http.StatusOK {
		return true, nil
	} else if res.StatusCode == http.StatusNotFound {
		return false, nil
	}
	err = fmt.Errorf("AYS returned status %d while getting service", res.StatusCode)
	return false, err

}

func (aystool AYStool) createBlueprint(repoName string, name string, bp map[string]interface{}) error {
	bpYaml, err := yaml.Marshal(bp)
	blueprint := ays.Blueprint{
		Content: string(bpYaml),
		Name:    name,
	}

	_, resp, err := aystool.Ays.CreateBlueprint(repoName, blueprint, nil, nil)
	if err != nil {
		return NewHTTPError(resp, err.Error())
	}

	if resp.StatusCode != http.StatusCreated && resp.StatusCode != http.StatusConflict {
		return NewHTTPError(resp, resp.Status)
	}

	return nil
}

func (aystool AYStool) executeBlueprint(blueprintName string, repoName string) (string, []string, error) {
	errBody := struct {
		Error string `json:"error"`
	}{}
	respData := struct {
		Msg               string   `json:"msg"`
		ProcessChangeJobs []string `json:"processChangeJobs"`
	}{}

	resp, err := aystool.Ays.ExecuteBlueprint(blueprintName, repoName, nil, nil)
	if err != nil {
		return "", nil, NewHTTPError(resp, err.Error())
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		if err := json.NewDecoder(resp.Body).Decode(&errBody); err != nil {
			return "", nil, NewHTTPError(resp, "Error decoding response body")
		}
		return "", nil, NewHTTPError(resp, errBody.Error)
	}
	if err := json.NewDecoder(resp.Body).Decode(&respData); err != nil {
		return "", nil, NewHTTPError(resp, "Error decoding response body")
	}

	return respData.Msg, respData.ProcessChangeJobs, nil
}

func (aystool AYStool) runRepo(repoName string) (*ays.AYSRun, error) {

	run, resp, err := aystool.Ays.CreateRun(repoName, nil, nil)
	if err != nil {
		return nil, NewHTTPError(resp, err.Error())
	}
	if resp.StatusCode != http.StatusOK {
		return nil, NewHTTPError(resp, resp.Status)
	}
	return &run, nil
}

func (aystool AYStool) archiveBlueprint(blueprintName string, repoName string) error {

	resp, err := aystool.Ays.ArchiveBlueprint(blueprintName, repoName, nil, nil)
	if err != nil {
		return NewHTTPError(resp, err.Error())
	}
	if resp.StatusCode != http.StatusOK {
		return NewHTTPError(resp, resp.Status)
	}
	return nil
}

func (aystool AYStool) getRun(runid, repoName string) (*ays.AYSRun, error) {
	run, resp, err := aystool.Ays.GetRun(runid, repoName, nil, nil)
	if err != nil {
		return nil, NewHTTPError(resp, err.Error())
	}

	if resp.StatusCode != http.StatusOK {
		return nil, NewHTTPError(resp, resp.Status)
	}

	if err = aystool.checkRun(run); err != nil {
		resp.StatusCode = http.StatusInternalServerError
		return nil, NewHTTPError(resp, err.Error())
	}
	return &run, nil
}

func (aystool AYStool) checkRun(run ays.AYSRun) error {
	var logs string
	if run.State == "error" {
		for _, step := range run.Steps {
			for _, job := range step.Jobs {
				for _, log := range job.Logs {
					logs = fmt.Sprintf("%s\n\n%s", logs, log.Log)
				}
			}
		}
		return errors.New(logs)
	}
	return nil
}
