package tools

import (
	"net/http"
	"time"

	ays "github.com/g8os/grid/api/ays-client"
)

var (
	ayscl *ays.AtYourServiceAPI
)

func SetAYSClient(client *ays.AtYourServiceAPI) {
	ayscl = client
}

//ExecuteBlueprint runs ays operations needed to run blueprints, if block is true, the function will block until the run is done
// create blueprint
// execute blueprint
// execute run
// archive the blueprint
func ExecuteBlueprint(repoName, blueprintName string, blueprint map[string]interface{}) (*ays.AYSRun, error) {

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

	for run.State == "new" || run.State == "running" {
		time.Sleep(time.Second)

		run, err = getRun(run.Key, repoName)
		if err != nil {
			return err
		}
	}
	return nil
}

func createBlueprint(repoName string, name string, bp map[string]interface{}) error {
	blueprint := ays.Blueprint{
		Content: bp,
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

	return &run, nil
}
