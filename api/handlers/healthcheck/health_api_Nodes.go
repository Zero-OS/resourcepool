package healthcheck

import (
	"encoding/json"
	"fmt"
	"sync"

	"github.com/zero-os/0-orchestrator/api/ays"
	client "github.com/zero-os/0-orchestrator/api/ays/ays-client"
	"github.com/zero-os/0-orchestrator/api/handlers"
	"github.com/zero-os/0-orchestrator/api/httperror"

	"net/http"
)

// ListNodesHealth is the handler for GET /health/nodes
// List NodesHealth
func (api *HealthCheckApi) ListNodesHealth(w http.ResponseWriter, r *http.Request) {
	// aysClient := tools.GetAysConnection(r, api)

	// queryParams := map[string]interface{}{
	// 	"fields": "hostname,id",
	// }
	// services, res, err := aysClient.Ays.ListServicesByRole("node.zero-os", api.AysRepo, nil, queryParams)
	// if !tools.HandleAYSResponse(err, res, w, "listing nodes health checks") {
	// 	return
	// }

	services, err := api.client.ListServices("node.zero-os", ays.ListServiceOpt{
		Fields: []string{"hostname", "id"},
	})
	if err != nil {
		handlers.HandleError(w, err)
		return
	}

	var (
		respBody = make([]*NodeHealthCheck, len(services))
		errs     = make([]error, len(services))
		wg       sync.WaitGroup
	)
	wg.Add(len(services))
	for i, service := range services {
		go func(i int, service *client.ServiceData) {
			defer wg.Done()
			info, err := api.getHealthCheck(service)
			if err != nil {
				errs[i] = err
			}

			respBody[i].Status = info.Status
			respBody[i].Hostname = info.Hostname
			respBody[i].ID = info.Name
		}(i, service)
		// var node Node
		// if err := json.Unmarshal(service.Data, &node); err != nil {
		// 	httperror.WriteError(w, http.StatusInternalServerError, err, "Error unmrshaling ays response")
		// 	return
		// }
		// respBody[i].ID = service.Name
		// respBody[i].Hostname = node.Hostname
		// healthstatus := "OK"

		// // Get healthcheck data
		// serviceName := fmt.Sprintf("node_%s", service.Name)
		// healthService, res, err := aysClient.Ays.GetServiceByName(serviceName, "healthcheck", api.AysRepo, nil, nil)
		// if !tools.HandleAYSResponse(err, res, w, "listing nodes health checks") {
		// 	return
		// }

		// var healthcheck HealthCheck
		// if err := json.Unmarshal(healthService.Data, &healthcheck); err != nil {
		// 	httperror.WriteError(w, http.StatusInternalServerError, err, "Error unmrshaling ays response")
		// 	return
		// }

		// for _, message := range healthcheck.Messages {
		// 	if message.Status != "OK" {
		// 		healthstatus = message.Status
		// 		if message.Status == "ERROR" {
		// 			break
		// 		}
		// 	}
		// }
		// respBody[i].Status = healthstatus

	}

	wg.Wait()

	for _, err := range errs {
		if err != nil {
			httperror.WriteError(w, http.StatusInternalServerError, err, err.Error())
			return
		}
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(&respBody)
}

type healthCheckInfo struct {
	NodeHealthCheck
	Name     string
	Hostname string
}

func (api *HealthCheckApi) getHealthCheck(service *client.ServiceData) (*healthCheckInfo, error) {
	var node Node
	if err := json.Unmarshal(service.Data, &node); err != nil {
		return nil, fmt.Errorf("Error unmrshaling ays response: %v", err)
	}

	info := &healthCheckInfo{}
	info.Name = service.Name
	info.Hostname = node.Hostname

	// Get healthcheck data
	serviceName := fmt.Sprintf("node_%s", service.Name)
	healthService, err := api.client.GetService("healthcheck", serviceName, "", nil)
	if err != nil {
		return nil, err
	}

	var healthcheck HealthCheck
	if err := json.Unmarshal(healthService.Data, &healthcheck); err != nil {
		return nil, fmt.Errorf("Error unmrshaling ays response: %v", err)
	}

	healthstatus := "OK"
	for _, message := range healthcheck.Messages {
		if message.Status != "OK" {
			healthstatus = message.Status
			if message.Status == "ERROR" {
				break
			}
		}
	}

	info.Status = healthstatus
	return info, nil
}
