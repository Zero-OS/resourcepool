package ays

// import (
// 	"fmt"
// 	"net/http"

// 	ays "github.com/zero-os/0-orchestrator/api/ays-client"
// 	"github.com/zero-os/0-orchestrator/api/httperror"
// )

// type Run struct {
// 	Runid string       `json:"runid" validate:"nonzero"`
// 	State EnumRunState `json:"state" validate:"nonzero"`
// }

// type EnumRunState string

// const (
// 	EnumRunStateok        EnumRunState = "ok"
// 	EnumRunStaterunning   EnumRunState = "running"
// 	EnumRunStatescheduled EnumRunState = "scheduled"
// 	EnumRunStateerror     EnumRunState = "error"
// 	EnumRunStatenew       EnumRunState = "new"
// 	EnumRunStatedisabled  EnumRunState = "disabled"
// 	EnumRunStatechanged   EnumRunState = "changed"
// )

// // WaitOnRun wait the end of execution of a run and deal with potential errors.
// func (aystool *AYStool) WaitOnRun(w http.ResponseWriter, aysRepo, runid string) (Run, error) {
// 	run, resp, err := aystool.Ays.GetRun(runid, aysRepo, nil, nil)
// 	if err != nil {
// 		httperror.WriteError(w, resp.StatusCode, err, "Error getting run")
// 		return Run{Runid: run.Key, State: EnumRunState(run.State)}, err
// 	}

// 	runstatus, err := aystool.WaitRunDone(run.Key, aysRepo)
// 	if err != nil {
// 		_, ok := err.(httperror.HTTPError)
// 		if !ok {
// 			errmsg := fmt.Sprintf("error waiting on run %s", run.Key)
// 			httperror.WriteError(w, http.StatusInternalServerError, err, errmsg)
// 			return Run{Runid: runstatus.Key, State: EnumRunState(runstatus.State)}, err
// 		}
// 	}

// 	var jobErr error
// 	var job ays.Job
// 	for _, step := range runstatus.Steps {
// 		if len(step.Jobs) > 0 {
// 			job := step.Jobs[0]
// 			if job.State == "error" {
// 				job, jobErr = aystool.ParseJobError(step.Jobs[0].Key, aysRepo)
// 				if jobErr != nil {
// 					break
// 				}
// 			}
// 		}
// 	}
// 	if jobErr != nil {
// 		httpErr, ok := jobErr.(httperror.HTTPError)
// 		if ok {
// 			httperror.WriteError(w, httpErr.Resp.StatusCode, httpErr, "")
// 			return Run{Runid: runstatus.Key, State: EnumRunState(runstatus.State)}, jobErr
// 		}
// 		errmsg := fmt.Sprintf("error waiting on job %s", job.Key)
// 		httperror.WriteError(w, http.StatusInternalServerError, err, errmsg)
// 		return Run{Runid: run.Key, State: EnumRunState(run.State)}, jobErr
// 	}

// 	if EnumRunState(runstatus.State) != EnumRunStateok {
// 		err = fmt.Errorf("Internal Server Error")
// 		httperror.WriteError(w, http.StatusInternalServerError, err, "")
// 		return Run{Runid: run.Key, State: EnumRunState(run.State)}, jobErr
// 	}
// 	response := Run{Runid: run.Key, State: EnumRunState(run.State)}
// 	return response, nil
// }

// func GetRunState(api API, w http.ResponseWriter, r *http.Request, runid string) (EnumRunState, error) {
// 	aysClient := GetAysConnection(r, api)
// 	aysRepo := api.AysRepoName()

// 	run, resp, err := aysClient.Ays.GetRun(runid, aysRepo, nil, nil)
// 	if err != nil {
// 		httperror.WriteError(w, resp.StatusCode, err, "Error getting run")
// 		return "", err
// 	}

// 	return EnumRunState(run.State), nil

// }
