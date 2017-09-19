package tools

import (
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"time"

	yaml "gopkg.in/yaml.v2"

	log "github.com/Sirupsen/logrus"
	ays "github.com/zero-os/0-orchestrator/api/ays-client"
	"github.com/zero-os/0-orchestrator/api/callback"
	"github.com/zero-os/0-orchestrator/api/httperror"
)

var (
	ayscl *ays.AtYourServiceAPI
)

type AYStool struct {
	Ays *ays.AysService
	// channel used to wait for run execution
	waitChan <-chan callback.CallbackStatus
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

func GetAYSClient(client *ays.AtYourServiceAPI) *AYStool {
	return &AYStool{
		Ays: client.Ays,
	}
}

func HandleAYSResponse(aysErr error, aysRes *http.Response, w http.ResponseWriter, action string) bool {
	if aysErr != nil {
		errmsg := fmt.Sprintf("AYS threw error while %s.\n", action)
		httperror.WriteError(w, http.StatusInternalServerError, aysErr, errmsg)
		return false
	}
	if aysRes.StatusCode != http.StatusOK {
		log.Errorf("AYS returned status %v while %s.\n", aysRes.StatusCode, action)
		w.WriteHeader(aysRes.StatusCode)
		return false
	}
	return true
}

func HandleExecuteBlueprintResponse(err error, w http.ResponseWriter, errmsg string) bool {
	if err == nil {
		return true
	}

	httpErr, ok := err.(httperror.HTTPError)
	if ok && httpErr.Resp != nil {
		if httpErr.Resp.StatusCode >= 400 && httpErr.Resp.StatusCode <= 499 {
			httperror.WriteError(w, httpErr.Resp.StatusCode, err, err.Error())
			return false
		}
		httperror.WriteError(w, httpErr.Resp.StatusCode, err, errmsg)
		return false
	}

	httperror.WriteError(w, http.StatusInternalServerError, err, errmsg)
	return false
}

//ExecuteBlueprint runs ays operations needed to run blueprints. This will BLOCK until blueprint job is complete.
// create blueprint
// execute blueprint
// execute run
// archive the blueprint
func (aystool *AYStool) ExecuteBlueprint(repoName, role, name, action string, blueprint map[string]interface{}) (*ays.AYSRun, error) {
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
func (aystool *AYStool) UpdateBlueprint(repoName, role, name, action string, blueprint map[string]interface{}) (string, error) {
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

func (aystool *AYStool) WaitRunDone(runid, repoName string) (*ays.AYSRun, error) {
	if aystool.waitChan != nil {
		// block until we have the callback
		// TODO: timeout to not wait forever ?
		log.Debugf("wait on run %s with callback", runid)
		i := 0
		for state := range aystool.waitChan {
			log.Debugf("callback received, run state: %v", state)
			//FIXME: find a way to know when ays stops retrying
			// now I count the retries
			if state == callback.CallbackStatusOk || i >= 6 {
				break
			}
			i++
		}

		return aystool.getRun(runid, repoName)
	}
	// no callback registered, do pooling
	log.Debugf("wait on run %s without callback", runid)
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

func (aystool *AYStool) WaitJobDone(jobid, repoName string) (ays.Job, error) {
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
	return aystool.ParseJobError(job.Key, repoName)
}

// I dont pass the job struct becasue ays does not pass the result even when in error unless a getjob api call is made on it.
// this will be fixed in ays 9.1.3 ?
func (aystool *AYStool) ParseJobError(jobKey string, repoName string) (ays.Job, error) {

	job, _, ayserr := aystool.Ays.GetJob(jobKey, repoName, nil, nil)
	if ayserr != nil {
		return job, ayserr
	}

	if job.Result == "" {
		return job, nil
	}

	err := AYSError{}
	if jsonErr := json.Unmarshal([]byte(job.Result), &err); jsonErr != nil {
		return job, jsonErr
	}

	err.err = fmt.Errorf(err.Message)
	errResp := http.Response{
		StatusCode: err.Code,
	}

	return job, httperror.New(&errResp, err.err.Error())
}

// ServiceExists check if an atyourserivce exists
func (aystool *AYStool) ServiceExists(serviceName string, instance string, repoName string) (bool, error) {
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

func (aystool *AYStool) createBlueprint(repoName string, name string, bp map[string]interface{}) error {
	bpYaml, err := yaml.Marshal(bp)
	blueprint := ays.Blueprint{
		Content: string(bpYaml),
		Name:    name,
	}

	_, resp, err := aystool.Ays.CreateBlueprint(repoName, blueprint, nil, nil)
	if err != nil {
		return httperror.New(resp, err.Error())
	}

	if resp.StatusCode != http.StatusCreated && resp.StatusCode != http.StatusConflict {
		return httperror.New(resp, resp.Status)
	}

	return nil
}

func (aystool *AYStool) executeBlueprint(blueprintName string, repoName string) (string, []string, error) {
	errBody := struct {
		Error string `json:"error"`
	}{}
	respData := struct {
		Msg               string   `json:"msg"`
		ProcessChangeJobs []string `json:"processChangeJobs"`
	}{}

	resp, err := aystool.Ays.ExecuteBlueprint(blueprintName, repoName, nil, nil)
	if err != nil {
		return "", nil, httperror.New(resp, err.Error())
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		if err := json.NewDecoder(resp.Body).Decode(&errBody); err != nil {
			return "", nil, httperror.New(resp, "Error decoding response body")
		}
		return "", nil, httperror.New(resp, errBody.Error)
	}
	if err := json.NewDecoder(resp.Body).Decode(&respData); err != nil {
		return "", nil, httperror.New(resp, "Error decoding response body")
	}

	return respData.Msg, respData.ProcessChangeJobs, nil
}

func (aystool *AYStool) runRepo(repoName string) (*ays.AYSRun, error) {
	var callbackURL string

	aystool.waitChan, callbackURL = callback.Register()
	queryParams := map[string]interface{}{
		"callback_url": callbackURL,
	}
	log.Debugf("create run with callback %s", callbackURL)

	run, resp, err := aystool.Ays.CreateRun(repoName, nil, queryParams)
	if err != nil {
		return nil, httperror.New(resp, err.Error())
	}
	if resp.StatusCode != http.StatusOK {
		return nil, httperror.New(resp, resp.Status)
	}
	return &run, nil
}

func (aystool *AYStool) archiveBlueprint(blueprintName string, repoName string) error {

	resp, err := aystool.Ays.ArchiveBlueprint(blueprintName, repoName, nil, nil)
	if err != nil {
		return httperror.New(resp, err.Error())
	}
	if resp.StatusCode != http.StatusOK {
		return httperror.New(resp, resp.Status)
	}
	return nil
}

func (aystool *AYStool) getRun(runid, repoName string) (*ays.AYSRun, error) {
	run, resp, err := aystool.Ays.GetRun(runid, repoName, nil, nil)
	if err != nil {
		return &run, httperror.New(resp, err.Error())
	}

	if resp.StatusCode != http.StatusOK {
		return &run, httperror.New(resp, resp.Status)
	}

	if err = aystool.checkRun(run); err != nil {
		resp.StatusCode = http.StatusInternalServerError
		return &run, httperror.New(resp, err.Error())
	}
	return &run, nil
}

func (aystool *AYStool) checkRun(run ays.AYSRun) error {
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
