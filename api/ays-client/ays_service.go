package client

import (
	"encoding/json"
	"net/http"
)

type AysService service

// reload AYS
func (s *AysService) Reload(headers, queryParams map[string]interface{}) (*http.Response, error) {

	resp, err := s.client.doReqWithBody("POST", s.client.BaseURI+"/ays/reload", nil, headers, queryParams)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	return resp, nil
}

// Get an actor by name
func (s *AysService) GetActorByName(actor, repository string, headers, queryParams map[string]interface{}) (Actor, *http.Response, error) {
	var u Actor

	resp, err := s.client.doReqNoBody("GET", s.client.BaseURI+"/ays/repository/"+repository+"/actor/"+actor, headers, queryParams)
	if err != nil {
		return u, nil, err
	}
	defer resp.Body.Close()

	return u, resp, json.NewDecoder(resp.Body).Decode(&u)
}

// update an actor from a template to the last version
func (s *AysService) UpdateActor(actor, repository string, headers, queryParams map[string]interface{}) (Actor, *http.Response, error) {
	var u Actor

	resp, err := s.client.doReqWithBody("PUT", s.client.BaseURI+"/ays/repository/"+repository+"/actor/"+actor, nil, headers, queryParams)
	if err != nil {
		return u, nil, err
	}
	defer resp.Body.Close()

	return u, resp, json.NewDecoder(resp.Body).Decode(&u)
}

// list all actors in the repository
func (s *AysService) ListActors(repository string, headers, queryParams map[string]interface{}) ([]NameListing, *http.Response, error) {
	var u []NameListing

	resp, err := s.client.doReqNoBody("GET", s.client.BaseURI+"/ays/repository/"+repository+"/actor", headers, queryParams)
	if err != nil {
		return u, nil, err
	}
	defer resp.Body.Close()

	return u, resp, json.NewDecoder(resp.Body).Decode(&u)
}

// delete a run
func (s *AysService) DeleteRun(runid, repository string, headers, queryParams map[string]interface{}) (*http.Response, error) {
	// create request object
	return s.client.doReqNoBody("DELETE", s.client.BaseURI+"/ays/repository/"+repository+"/aysrun/"+runid, headers, queryParams)
}

// Get an aysrun
func (s *AysService) GetRun(runid, repository string, headers, queryParams map[string]interface{}) (AYSRun, *http.Response, error) {
	var u AYSRun

	resp, err := s.client.doReqNoBody("GET", s.client.BaseURI+"/ays/repository/"+repository+"/aysrun/"+runid, headers, queryParams)
	if err != nil {
		return u, nil, err
	}
	defer resp.Body.Close()

	return u, resp, json.NewDecoder(resp.Body).Decode(&u)
}

// execute an aysrun
func (s *AysService) ExecuteRun(runid, repository string, headers, queryParams map[string]interface{}) (AYSRun, *http.Response, error) {
	var u AYSRun

	resp, err := s.client.doReqWithBody("POST", s.client.BaseURI+"/ays/repository/"+repository+"/aysrun/"+runid, nil, headers, queryParams)
	if err != nil {
		return u, nil, err
	}
	defer resp.Body.Close()

	return u, resp, json.NewDecoder(resp.Body).Decode(&u)
}

// list all runs of the repository
func (s *AysService) ListRuns(repository string, headers, queryParams map[string]interface{}) ([]AYSRunListing, *http.Response, error) {
	var u []AYSRunListing

	resp, err := s.client.doReqNoBody("GET", s.client.BaseURI+"/ays/repository/"+repository+"/aysrun", headers, queryParams)
	if err != nil {
		return u, nil, err
	}
	defer resp.Body.Close()

	return u, resp, json.NewDecoder(resp.Body).Decode(&u)
}

// Create a run based on all the action scheduled. This call returns an AYSRun object describing what is going to hapen on the repository.
// This is an asyncronous call. To be notify of the status of the run when then execution is finised or when an error occurs, you need to specify a callback url.
// A post request will be send to this callback url with the status of the run and the key of the run. Using this key you can inspect in detail the result of the run
// using the 'GET /ays/repository/{repository}/aysrun/{aysrun_key}' endpoint
func (s *AysService) CreateRun(repository string, headers, queryParams map[string]interface{}) (AYSRun, *http.Response, error) {
	var u AYSRun

	resp, err := s.client.doReqWithBody("POST", s.client.BaseURI+"/ays/repository/"+repository+"/aysrun", nil, headers, queryParams)
	if err != nil {
		return u, nil, err
	}
	defer resp.Body.Close()

	return u, resp, json.NewDecoder(resp.Body).Decode(&u)
}

// archive the blueprint
func (s *AysService) ArchiveBlueprint(blueprint, repository string, headers, queryParams map[string]interface{}) (*http.Response, error) {

	resp, err := s.client.doReqWithBody("PUT", s.client.BaseURI+"/ays/repository/"+repository+"/blueprint/"+blueprint+"/archive", nil, headers, queryParams)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	return resp, nil
}

// restore the blueprint
func (s *AysService) RestoreBlueprint(blueprint, repository string, headers, queryParams map[string]interface{}) (*http.Response, error) {

	resp, err := s.client.doReqWithBody("PUT", s.client.BaseURI+"/ays/repository/"+repository+"/blueprint/"+blueprint+"/restore", nil, headers, queryParams)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	return resp, nil
}

// delete blueprint
func (s *AysService) DeleteBlueprint(blueprint, repository string, headers, queryParams map[string]interface{}) (*http.Response, error) {
	// create request object
	return s.client.doReqNoBody("DELETE", s.client.BaseURI+"/ays/repository/"+repository+"/blueprint/"+blueprint, headers, queryParams)
}

// Get a blueprint
func (s *AysService) GetBlueprint(blueprint, repository string, headers, queryParams map[string]interface{}) (Blueprint, *http.Response, error) {
	var u Blueprint

	resp, err := s.client.doReqNoBody("GET", s.client.BaseURI+"/ays/repository/"+repository+"/blueprint/"+blueprint, headers, queryParams)
	if err != nil {
		return u, nil, err
	}
	defer resp.Body.Close()

	return u, resp, json.NewDecoder(resp.Body).Decode(&u)
}

// Execute the blueprint
func (s *AysService) ExecuteBlueprint(blueprint, repository string, body AysRepositoryRepositoryBlueprintBlueprintPostReqBody, headers, queryParams map[string]interface{}) (*http.Response, error) {

	resp, err := s.client.doReqWithBody("POST", s.client.BaseURI+"/ays/repository/"+repository+"/blueprint/"+blueprint, &body, headers, queryParams)
	if err != nil {
		return nil, err
	}

	return resp, nil
}

// Update existing blueprint
func (s *AysService) UpdateBlueprint(blueprint, repository string, body AysRepositoryRepositoryBlueprintBlueprintPutReqBody, headers, queryParams map[string]interface{}) (*http.Response, error) {

	resp, err := s.client.doReqWithBody("PUT", s.client.BaseURI+"/ays/repository/"+repository+"/blueprint/"+blueprint, &body, headers, queryParams)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	return resp, nil
}

// List all blueprint
func (s *AysService) ListBlueprints(repository string, headers, queryParams map[string]interface{}) ([]BlueprintListing, *http.Response, error) {
	var u []BlueprintListing

	resp, err := s.client.doReqNoBody("GET", s.client.BaseURI+"/ays/repository/"+repository+"/blueprint", headers, queryParams)
	if err != nil {
		return u, nil, err
	}
	defer resp.Body.Close()

	return u, resp, json.NewDecoder(resp.Body).Decode(&u)
}

// Create a new blueprint
func (s *AysService) CreateBlueprint(repository string, body Blueprint, headers, queryParams map[string]interface{}) (AysRepositoryRepositoryBlueprintPostRespBody, *http.Response, error) {
	var u AysRepositoryRepositoryBlueprintPostRespBody

	resp, err := s.client.doReqWithBody("POST", s.client.BaseURI+"/ays/repository/"+repository+"/blueprint", &body, headers, queryParams)
	if err != nil {
		return u, nil, err
	}
	defer resp.Body.Close()

	return u, resp, json.NewDecoder(resp.Body).Decode(&u)
}

// destroy repo without deleting it from FS
func (s *AysService) DestroyRepository(repository string, headers, queryParams map[string]interface{}) (*http.Response, error) {

	resp, err := s.client.doReqWithBody("POST", s.client.BaseURI+"/ays/repository/"+repository+"/destroy", nil, headers, queryParams)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	return resp, nil
}

// Get a jobid
func (s *AysService) GetJob(jobid, repository string, headers, queryParams map[string]interface{}) (Job, *http.Response, error) {
	var u Job

	resp, err := s.client.doReqNoBody("GET", s.client.BaseURI+"/ays/repository/"+repository+"/job/"+jobid, headers, queryParams)
	if err != nil {
		return u, nil, err
	}
	defer resp.Body.Close()

	return u, resp, json.NewDecoder(resp.Body).Decode(&u)
}

// List all jobs of the repository that match the filters
func (s *AysService) ListJobs(repository string, headers, queryParams map[string]interface{}) ([]JobData, *http.Response, error) {
	var u []JobData

	resp, err := s.client.doReqNoBody("GET", s.client.BaseURI+"/ays/repository/"+repository+"/job", headers, queryParams)
	if err != nil {
		return u, nil, err
	}
	defer resp.Body.Close()

	return u, resp, json.NewDecoder(resp.Body).Decode(&u)
}

// delete a service and all its children
func (s *AysService) DeleteServiceByName(name, role, repository string, headers, queryParams map[string]interface{}) (*http.Response, error) {
	// create request object
	return s.client.doReqNoBody("DELETE", s.client.BaseURI+"/ays/repository/"+repository+"/service/"+role+"/"+name, headers, queryParams)
}

// Get a service by its name
func (s *AysService) GetServiceByName(name, role, repository string, headers, queryParams map[string]interface{}) (Service, *http.Response, error) {
	var u Service

	resp, err := s.client.doReqNoBody("GET", s.client.BaseURI+"/ays/repository/"+repository+"/service/"+role+"/"+name, headers, queryParams)
	if err != nil {
		return u, nil, err
	}
	defer resp.Body.Close()

	return u, resp, json.NewDecoder(resp.Body).Decode(&u)
}

// List all services of role 'role' in the repository
func (s *AysService) ListServicesByRole(role, repository string, headers, queryParams map[string]interface{}) ([]ServiceData, *http.Response, error) {
	var u []ServiceData

	resp, err := s.client.doReqNoBody("GET", s.client.BaseURI+"/ays/repository/"+repository+"/service/"+role, headers, queryParams)
	if err != nil {
		return u, nil, err
	}
	defer resp.Body.Close()

	return u, resp, json.NewDecoder(resp.Body).Decode(&u)
}

// List all services in the repository
func (s *AysService) ListServices(repository string, headers, queryParams map[string]interface{}) ([]ServicePointer, *http.Response, error) {
	var u []ServicePointer

	resp, err := s.client.doReqNoBody("GET", s.client.BaseURI+"/ays/repository/"+repository+"/service", headers, queryParams)
	if err != nil {
		return u, nil, err
	}
	defer resp.Body.Close()

	return u, resp, json.NewDecoder(resp.Body).Decode(&u)
}

// update all templates in a repository
func (s *AysService) UpdateTemplates(repository string, headers, queryParams map[string]interface{}) (AysRepositoryRepositoryTemplateUpdateGetRespBody, *http.Response, error) {
	var u AysRepositoryRepositoryTemplateUpdateGetRespBody

	resp, err := s.client.doReqNoBody("GET", s.client.BaseURI+"/ays/repository/"+repository+"/template/update", headers, queryParams)
	if err != nil {
		return u, nil, err
	}
	defer resp.Body.Close()

	return u, resp, json.NewDecoder(resp.Body).Decode(&u)
}

// Get a template
func (s *AysService) GetTemplate(name, repository string, headers, queryParams map[string]interface{}) (Template, *http.Response, error) {
	var u Template

	resp, err := s.client.doReqNoBody("GET", s.client.BaseURI+"/ays/repository/"+repository+"/template/"+name, headers, queryParams)
	if err != nil {
		return u, nil, err
	}
	defer resp.Body.Close()

	return u, resp, json.NewDecoder(resp.Body).Decode(&u)
}

// list all templates
func (s *AysService) ListTemplates(repository string, headers, queryParams map[string]interface{}) ([]TemplateListing, *http.Response, error) {
	var u []TemplateListing

	resp, err := s.client.doReqNoBody("GET", s.client.BaseURI+"/ays/repository/"+repository+"/template", headers, queryParams)
	if err != nil {
		return u, nil, err
	}
	defer resp.Body.Close()

	return u, resp, json.NewDecoder(resp.Body).Decode(&u)
}

// Delete a repository
func (s *AysService) DeleteRepository(repository string, headers, queryParams map[string]interface{}) (*http.Response, error) {
	// create request object
	return s.client.doReqNoBody("DELETE", s.client.BaseURI+"/ays/repository/"+repository, headers, queryParams)
}

// Get information of a repository
func (s *AysService) GetRepository(repository string, headers, queryParams map[string]interface{}) (Repository, *http.Response, error) {
	var u Repository

	resp, err := s.client.doReqNoBody("GET", s.client.BaseURI+"/ays/repository/"+repository, headers, queryParams)
	if err != nil {
		return u, nil, err
	}
	defer resp.Body.Close()

	return u, resp, json.NewDecoder(resp.Body).Decode(&u)
}

// list all repositorys
func (s *AysService) ListRepositories(headers, queryParams map[string]interface{}) ([]string, *http.Response, error) {
	var u []string

	resp, err := s.client.doReqNoBody("GET", s.client.BaseURI+"/ays/repository", headers, queryParams)
	if err != nil {
		return u, nil, err
	}
	defer resp.Body.Close()

	return u, resp, json.NewDecoder(resp.Body).Decode(&u)
}

// create a new repository
func (s *AysService) CreateRepository(body AysRepositoryPostReqBody, headers, queryParams map[string]interface{}) (Repository, *http.Response, error) {
	var u Repository

	resp, err := s.client.doReqWithBody("POST", s.client.BaseURI+"/ays/repository", &body, headers, queryParams)
	if err != nil {
		return u, nil, err
	}
	defer resp.Body.Close()

	return u, resp, json.NewDecoder(resp.Body).Decode(&u)
}

// add a new actor template repository
func (s *AysService) AddTemplateRepo(body TemplateRepo, headers, queryParams map[string]interface{}) (TemplateRepo, *http.Response, error) {
	var u TemplateRepo

	resp, err := s.client.doReqWithBody("POST", s.client.BaseURI+"/ays/template_repo", &body, headers, queryParams)
	if err != nil {
		return u, nil, err
	}
	defer resp.Body.Close()

	return u, resp, json.NewDecoder(resp.Body).Decode(&u)
}

// get an AYS template
func (s *AysService) GetAYSTemplate(name string, headers, queryParams map[string]interface{}) (Template, *http.Response, error) {
	var u Template

	resp, err := s.client.doReqNoBody("GET", s.client.BaseURI+"/ays/templates/"+name, headers, queryParams)
	if err != nil {
		return u, nil, err
	}
	defer resp.Body.Close()

	return u, resp, json.NewDecoder(resp.Body).Decode(&u)
}

// list all AYS templates
func (s *AysService) ListAYSTemplates(headers, queryParams map[string]interface{}) ([]TemplateListing, *http.Response, error) {
	var u []TemplateListing

	resp, err := s.client.doReqNoBody("GET", s.client.BaseURI+"/ays/templates", headers, queryParams)
	if err != nil {
		return u, nil, err
	}
	defer resp.Body.Close()

	return u, resp, json.NewDecoder(resp.Body).Decode(&u)
}
