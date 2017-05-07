package tools

import (
	"errors"
	"fmt"
	"net/http"
	"time"

	yaml "gopkg.in/yaml.v2"

	ays "github.com/g8os/resourcepool/api/ays-client"
)

var (
	ayscl *ays.AtYourServiceAPI
)

func SetAYSClient(client *ays.AtYourServiceAPI) {
	ayscl = client
}

type ActionBlock struct {
	Action  string `json:"action"`
	Actor   string `json:"actor"`
	Service string `json:"service"`
	Force   bool   `json:"force" validate:"omitempty"`
}

//ExecuteBlueprint runs ays operations needed to run blueprints, if block is true, the function will block until the run is done
// create blueprint
// execute blueprint
// execute run
// archive the blueprint
func ExecuteBlueprint(repoName, role, name, action string, blueprint map[string]interface{}) (*ays.AYSRun, error) {
	blueprintName := fmt.Sprintf("%s_%s_%s_%+v", role, name, action, time.Now().Unix())

	if err := createBlueprint(repoName, blueprintName, blueprint); err != nil {
		return nil, err
	}

	if err := executeBlueprint(blueprintName, repoName); err != nil {
		archiveBlueprint(blueprintName, repoName)
		return nil, err
	}

	run, err := runRepo(repoName)
	if err != nil {
		archiveBlueprint(blueprintName, repoName)
		return nil, err
	}

	return run, archiveBlueprint(blueprintName, repoName)
}

func WaitRunDone(runid, repoName string) error {
	run, err := getRun(runid, repoName)

	if err != nil {
		return err
	}

	for run.State == "new" || run.State == "running" {
		time.Sleep(time.Second)

		run, err = getRun(run.Key, repoName)
		if err != nil {
			return err
		}
	}
	return nil
}

// ServiceExists check if an atyourserivce exists
func ServiceExists(serviceName string, instance string, repoName string) (bool, error) {
	_, res, err := ayscl.Ays.GetServiceByName(instance, serviceName, repoName, nil, nil)
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

func createBlueprint(repoName string, name string, bp map[string]interface{}) error {
	bpYaml, err := yaml.Marshal(bp)
	blueprint := ays.Blueprint{
		Content: string(bpYaml),
		Name:    name,
	}

	_, resp, err := ayscl.Ays.CreateBlueprint(repoName, blueprint, nil, nil)
	if err != nil {
		return NewHTTPError(resp, err.Error())
	}

	if resp.StatusCode != http.StatusCreated && resp.StatusCode != http.StatusConflict {
		return NewHTTPError(resp, resp.Status)
	}

	return nil
}

func executeBlueprint(blueprintName string, repoName string) error {

	resp, err := ayscl.Ays.ExecuteBlueprint(blueprintName, repoName, nil, nil)
	if err != nil {
		return NewHTTPError(resp, err.Error())
	}
	if resp.StatusCode != http.StatusOK {
		return NewHTTPError(resp, resp.Status)
	}
	return nil
}

func runRepo(repoName string) (*ays.AYSRun, error) {

	run, resp, err := ayscl.Ays.CreateRun(repoName, nil, nil)
	if err != nil {
		return nil, NewHTTPError(resp, err.Error())
	}
	if resp.StatusCode != http.StatusOK {
		return nil, NewHTTPError(resp, resp.Status)
	}
	return &run, nil
}

func archiveBlueprint(blueprintName string, repoName string) error {

	resp, err := ayscl.Ays.ArchiveBlueprint(blueprintName, repoName, nil, nil)
	if err != nil {
		return NewHTTPError(resp, err.Error())
	}
	if resp.StatusCode != http.StatusOK {
		return NewHTTPError(resp, resp.Status)
	}
	return nil
}

func getRun(runid, repoName string) (*ays.AYSRun, error) {
	run, resp, err := ayscl.Ays.GetRun(runid, repoName, nil, nil)
	if err != nil {
		return nil, NewHTTPError(resp, err.Error())
	}

	if resp.StatusCode != http.StatusOK {
		return nil, NewHTTPError(resp, resp.Status)
	}

	if err = checkRun(run); err != nil {
		resp.StatusCode = http.StatusInternalServerError
		return nil, NewHTTPError(resp, err.Error())
	}
	return &run, nil
}

func checkRun(run ays.AYSRun) error {
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
