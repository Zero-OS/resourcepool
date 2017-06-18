package tools

import (
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

//ExecuteBlueprint runs ays operations needed to run blueprints, if block is true, the function will block until the run is done
// create blueprint
// execute blueprint
// execute run
// archive the blueprint
func (aystool AYStool) ExecuteBlueprint(repoName, role, name, action string, blueprint map[string]interface{}) (*ays.AYSRun, error) {
	blueprintName := fmt.Sprintf("%s_%s_%s_%+v", role, name, action, time.Now().Unix())

	if err := aystool.createBlueprint(repoName, blueprintName, blueprint); err != nil {
		return nil, err
	}

	if err := aystool.executeBlueprint(blueprintName, repoName); err != nil {
		aystool.archiveBlueprint(blueprintName, repoName)
		return nil, err
	}

	run, err := aystool.runRepo(repoName)
	if err != nil {
		aystool.archiveBlueprint(blueprintName, repoName)
		return nil, err
	}

	return run, aystool.archiveBlueprint(blueprintName, repoName)
}

func (aystool AYStool) WaitRunDone(runid, repoName string) error {
	run, err := aystool.getRun(runid, repoName)

	if err != nil {
		return err
	}

	for run.State == "new" || run.State == "running" {
		time.Sleep(time.Second)

		run, err = aystool.getRun(run.Key, repoName)
		if err != nil {
			return err
		}
	}
	return nil
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

func (aystool AYStool) executeBlueprint(blueprintName string, repoName string) error {

	resp, err := aystool.Ays.ExecuteBlueprint(blueprintName, repoName, nil, nil)
	if err != nil {
		return NewHTTPError(resp, err.Error())
	}
	if resp.StatusCode != http.StatusOK {
		return NewHTTPError(resp, resp.Status)
	}
	return nil
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
