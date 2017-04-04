package main

import (
	"encoding/json"
	"net/http"

	client "github.com/g8os/grid/ays-client"
)

// ExecuteBlueprint runs ays operations needed to run blueprints
func ExecuteBlueprint(w http.ResponseWriter, blueprintName string, blueprint map[string]interface{}) {
	repoName := AysRepo
	if !createRepo(w, repoName) {
		return
	}

	if !createBlueprint(w, repoName, blueprintName, blueprint) {
		return
	}

	if !executeBlueprint(w, blueprintName, repoName) {
		archiveBlueprint(w, blueprintName, repoName)
		return
	}

	if !runRepo(w, repoName) {
		archiveBlueprint(w, blueprintName, repoName)
		return
	}

	archiveBlueprint(w, blueprintName, repoName)
}

func createRepo(w http.ResponseWriter, repoName string) bool {
	cl := client.NewAtYourServiceAPI()
	// Create ays repo
	var repo client.AysRepositoryPostReqBody
	repo.Name = repoName
	repo.Git_url = "https://github.com/g8os/test"

	_, resp, err := cl.Ays.CreateRepository(repo, nil, nil)

	if err != nil {
		WriteError(w, http.StatusInternalServerError, err)
		return false
	}
	if resp.StatusCode != http.StatusCreated && resp.StatusCode != http.StatusConflict {
		w.WriteHeader(resp.StatusCode)
		return false
	}
	return true
}

func createBlueprint(w http.ResponseWriter, repoName string, name string, bp map[string]interface{}) bool {
	cl := client.NewAtYourServiceAPI()

	data, _ := json.Marshal(bp)
	raw := json.RawMessage(data)

	var blueprint client.Blueprint

	blueprint.Content = raw
	blueprint.Name = name
	_, resp, err := cl.Ays.CreateBlueprint(repoName, blueprint, nil, nil)
	if err != nil {
		WriteError(w, http.StatusInternalServerError, err)
		return false
	}
	if resp.StatusCode != http.StatusCreated && resp.StatusCode != http.StatusConflict {
		w.WriteHeader(resp.StatusCode)
		return false
	}
	return true
}

func executeBlueprint(w http.ResponseWriter, blueprintName string, repoName string) bool {
	cl := client.NewAtYourServiceAPI()

	resp, err := cl.Ays.ExecuteBlueprint(blueprintName, repoName, nil, nil)
	if err != nil {
		WriteError(w, http.StatusInternalServerError, err)
		return false
	}
	if resp.StatusCode != http.StatusOK {
		w.WriteHeader(resp.StatusCode)
		return false
	}
	return true
}

func runRepo(w http.ResponseWriter, repoName string) bool {
	cl := client.NewAtYourServiceAPI()
	_, resp, err := cl.Ays.CreateRun(repoName, nil, nil)
	if err != nil {
		WriteError(w, http.StatusInternalServerError, err)
		return false
	}
	if resp.StatusCode != http.StatusOK {
		w.WriteHeader(resp.StatusCode)
		return false
	}
	return true
}

func archiveBlueprint(w http.ResponseWriter, blueprintName string, repoName string) bool {
	cl := client.NewAtYourServiceAPI()
	resp, err := cl.Ays.ArchiveBlueprint(blueprintName, repoName, nil, nil)
	if err != nil {
		WriteError(w, http.StatusInternalServerError, err)
		return false
	}
	if resp.StatusCode != http.StatusOK {
		w.WriteHeader(resp.StatusCode)
		return false
	}
	return true
}
