package client

import (
	"encoding/json"
	"net/http"
)

type AysService service

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
func (s *AysService) CreateRepository(aysrepositorypostreqbody AysRepositoryPostReqBody, headers, queryParams map[string]interface{}) (Repository, *http.Response, error) {
	var u Repository

	resp, err := s.client.doReqWithBody("POST", s.client.BaseURI+"/ays/repository", &aysrepositorypostreqbody, headers, queryParams)
	if err != nil {
		return u, nil, err
	}
	defer resp.Body.Close()

	return u, resp, json.NewDecoder(resp.Body).Decode(&u)
}

// Get information of a repository
func (s *AysService) GetRepository(repository_name string, headers, queryParams map[string]interface{}) (Repository, *http.Response, error) {
	var u Repository

	resp, err := s.client.doReqNoBody("GET", s.client.BaseURI+"/ays/repository/"+repository_name, headers, queryParams)
	if err != nil {
		return u, nil, err
	}
	defer resp.Body.Close()

	return u, resp, json.NewDecoder(resp.Body).Decode(&u)
}

// Delete a repository
func (s *AysService) DeleteRepository(repository_name string, headers, queryParams map[string]interface{}) (*http.Response, error) {
	// create request object
	return s.client.doReqNoBody("DELETE", s.client.BaseURI+"/ays/repository/"+repository_name, headers, queryParams)
}

// list all actors in the repository
func (s *AysService) ListActors(repository_name string, headers, queryParams map[string]interface{}) ([]NameListing, *http.Response, error) {
	var u []NameListing

	resp, err := s.client.doReqNoBody("GET", s.client.BaseURI+"/ays/repository/"+repository_name+"/actor", headers, queryParams)
	if err != nil {
		return u, nil, err
	}
	defer resp.Body.Close()

	return u, resp, json.NewDecoder(resp.Body).Decode(&u)
}

// update an actor from a template to the last version
func (s *AysService) UpdateActor(actor_name, repository_name string, headers, queryParams map[string]interface{}) (Actor, *http.Response, error) {
	var u Actor

	resp, err := s.client.doReqWithBody("PUT", s.client.BaseURI+"/ays/repository/"+repository_name+"/actor/"+actor_name, nil, headers, queryParams)
	if err != nil {
		return u, nil, err
	}
	defer resp.Body.Close()

	return u, resp, json.NewDecoder(resp.Body).Decode(&u)
}

// Get an actor by name
func (s *AysService) GetActorByName(actor_name, repository_name string, headers, queryParams map[string]interface{}) (Actor, *http.Response, error) {
	var u Actor

	resp, err := s.client.doReqNoBody("GET", s.client.BaseURI+"/ays/repository/"+repository_name+"/actor/"+actor_name, headers, queryParams)
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
func (s *AysService) CreateRun(repository_name string, headers, queryParams map[string]interface{}) (AYSRun, *http.Response, error) {
	var u AYSRun

	resp, err := s.client.doReqWithBody("POST", s.client.BaseURI+"/ays/repository/"+repository_name+"/aysrun", nil, headers, queryParams)
	if err != nil {
		return u, nil, err
	}
	defer resp.Body.Close()

	return u, resp, json.NewDecoder(resp.Body).Decode(&u)
}

// list all runs of the repository
func (s *AysService) ListRuns(repository_name string, headers, queryParams map[string]interface{}) ([]AYSRunListing, *http.Response, error) {
	var u []AYSRunListing

	resp, err := s.client.doReqNoBody("GET", s.client.BaseURI+"/ays/repository/"+repository_name+"/aysrun", headers, queryParams)
	if err != nil {
		return u, nil, err
	}
	defer resp.Body.Close()

	return u, resp, json.NewDecoder(resp.Body).Decode(&u)
}

// Get an aysrun
func (s *AysService) GetRun(runid, repository_name string, headers, queryParams map[string]interface{}) (AYSRun, *http.Response, error) {
	var u AYSRun

	resp, err := s.client.doReqNoBody("GET", s.client.BaseURI+"/ays/repository/"+repository_name+"/aysrun/"+runid, headers, queryParams)
	if err != nil {
		return u, nil, err
	}
	defer resp.Body.Close()

	return u, resp, json.NewDecoder(resp.Body).Decode(&u)
}

// List all blueprint
func (s *AysService) ListBlueprints(repository_name string, headers, queryParams map[string]interface{}) ([]BlueprintListing, *http.Response, error) {
	var u []BlueprintListing

	resp, err := s.client.doReqNoBody("GET", s.client.BaseURI+"/ays/repository/"+repository_name+"/blueprint", headers, queryParams)
	if err != nil {
		return u, nil, err
	}
	defer resp.Body.Close()

	return u, resp, json.NewDecoder(resp.Body).Decode(&u)
}

// Create a new blueprint
func (s *AysService) CreateBlueprint(repository_name string, blueprint Blueprint, headers, queryParams map[string]interface{}) (AysRepositoryRepository_nameBlueprintPostRespBody, *http.Response, error) {
	var u AysRepositoryRepository_nameBlueprintPostRespBody

	resp, err := s.client.doReqWithBody("POST", s.client.BaseURI+"/ays/repository/"+repository_name+"/blueprint", &blueprint, headers, queryParams)
	if err != nil {
		return u, nil, err
	}
	defer resp.Body.Close()

	return u, resp, json.NewDecoder(resp.Body).Decode(&u)
}

// delete blueprint
func (s *AysService) DeleteBlueprint(blueprint_name, repository_name string, headers, queryParams map[string]interface{}) (*http.Response, error) {
	// create request object
	return s.client.doReqNoBody("DELETE", s.client.BaseURI+"/ays/repository/"+repository_name+"/blueprint/"+blueprint_name, headers, queryParams)
}

// Get a blueprint
func (s *AysService) GetBlueprint(blueprint_name, repository_name string, headers, queryParams map[string]interface{}) (Blueprint, *http.Response, error) {
	var u Blueprint

	resp, err := s.client.doReqNoBody("GET", s.client.BaseURI+"/ays/repository/"+repository_name+"/blueprint/"+blueprint_name, headers, queryParams)
	if err != nil {
		return u, nil, err
	}
	defer resp.Body.Close()

	return u, resp, json.NewDecoder(resp.Body).Decode(&u)
}

// Update existing blueprint
func (s *AysService) UpdateBlueprint(blueprint_name, repository_name string, aysrepositoryrepository_nameblueprintblueprint_nameputreqbody AysRepositoryRepository_nameBlueprintBlueprint_namePutReqBody, headers, queryParams map[string]interface{}) (*http.Response, error) {

	resp, err := s.client.doReqWithBody("PUT", s.client.BaseURI+"/ays/repository/"+repository_name+"/blueprint/"+blueprint_name, &aysrepositoryrepository_nameblueprintblueprint_nameputreqbody, headers, queryParams)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	return resp, nil
}

// Execute the blueprint
func (s *AysService) ExecuteBlueprint(blueprint_name, repository_name string, headers, queryParams map[string]interface{}) (*http.Response, error) {

	resp, err := s.client.doReqWithBody("POST", s.client.BaseURI+"/ays/repository/"+repository_name+"/blueprint/"+blueprint_name, nil, headers, queryParams)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	return resp, nil
}

// archive the blueprint
func (s *AysService) ArchiveBlueprint(blueprint_name, repository_name string, headers, queryParams map[string]interface{}) (*http.Response, error) {

	resp, err := s.client.doReqWithBody("PUT", s.client.BaseURI+"/ays/repository/"+repository_name+"/blueprint/"+blueprint_name+"/archive", nil, headers, queryParams)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	return resp, nil
}

// restore the blueprint
func (s *AysService) RestoreBlueprint(blueprint_name, repository_name string, headers, queryParams map[string]interface{}) (*http.Response, error) {

	resp, err := s.client.doReqWithBody("PUT", s.client.BaseURI+"/ays/repository/"+repository_name+"/blueprint/"+blueprint_name+"/restore", nil, headers, queryParams)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	return resp, nil
}

// List all services in the repository
func (s *AysService) ListServices(repository_name string, headers, queryParams map[string]interface{}) ([]ServicePointer, *http.Response, error) {
	var u []ServicePointer

	resp, err := s.client.doReqNoBody("GET", s.client.BaseURI+"/ays/repository/"+repository_name+"/service", headers, queryParams)
	if err != nil {
		return u, nil, err
	}
	defer resp.Body.Close()

	return u, resp, json.NewDecoder(resp.Body).Decode(&u)
}

// List all services of role 'role' in the repository
func (s *AysService) ListServicesByRole(service_role, repository_name string, headers, queryParams map[string]interface{}) ([]ServicePointer, *http.Response, error) {
	var u []ServicePointer

	resp, err := s.client.doReqNoBody("GET", s.client.BaseURI+"/ays/repository/"+repository_name+"/service/"+service_role, headers, queryParams)
	if err != nil {
		return u, nil, err
	}
	defer resp.Body.Close()

	return u, resp, json.NewDecoder(resp.Body).Decode(&u)
}

// delete a service and all its children
func (s *AysService) DeleteServiceByName(service_name, service_role, repository_name string, headers, queryParams map[string]interface{}) (*http.Response, error) {
	// create request object
	return s.client.doReqNoBody("DELETE", s.client.BaseURI+"/ays/repository/"+repository_name+"/service/"+service_role+"/"+service_name, headers, queryParams)
}

// Get a service by its name
func (s *AysService) GetServiceByName(service_name, service_role, repository_name string, headers, queryParams map[string]interface{}) (Service, *http.Response, error) {
	var u Service

	resp, err := s.client.doReqNoBody("GET", s.client.BaseURI+"/ays/repository/"+repository_name+"/service/"+service_role+"/"+service_name, headers, queryParams)
	if err != nil {
		return u, nil, err
	}
	defer resp.Body.Close()

	return u, resp, json.NewDecoder(resp.Body).Decode(&u)
}

// list all templates
func (s *AysService) ListTemplates(repository_name string, headers, queryParams map[string]interface{}) ([]TemplateListing, *http.Response, error) {
	var u []TemplateListing

	resp, err := s.client.doReqNoBody("GET", s.client.BaseURI+"/ays/repository/"+repository_name+"/template", headers, queryParams)
	if err != nil {
		return u, nil, err
	}
	defer resp.Body.Close()

	return u, resp, json.NewDecoder(resp.Body).Decode(&u)
}

// Get a template
func (s *AysService) GetTemplate(template_name, repository_name string, headers, queryParams map[string]interface{}) (Template, *http.Response, error) {
	var u Template

	resp, err := s.client.doReqNoBody("GET", s.client.BaseURI+"/ays/repository/"+repository_name+"/template/"+template_name, headers, queryParams)
	if err != nil {
		return u, nil, err
	}
	defer resp.Body.Close()

	return u, resp, json.NewDecoder(resp.Body).Decode(&u)
}

// add a new actor template repository
func (s *AysService) AddTemplateRepo(templaterepo TemplateRepo, headers, queryParams map[string]interface{}) (TemplateRepo, *http.Response, error) {
	var u TemplateRepo

	resp, err := s.client.doReqWithBody("POST", s.client.BaseURI+"/ays/template_repo", &templaterepo, headers, queryParams)
	if err != nil {
		return u, nil, err
	}
	defer resp.Body.Close()

	return u, resp, json.NewDecoder(resp.Body).Decode(&u)
}
