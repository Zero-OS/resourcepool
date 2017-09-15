package callback

import (
	"bytes"
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"sync"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestCallBack(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()
	cbRountine := newCallbackRoutine(ctx, "localhost:8080")

	runid := "testrunid"
	cbChan, cbURL := cbRountine.register(runid)
	assert.Equal(t, cbURL, "http://localhost:8080/callback?uuid=testrunid")

	wg := sync.WaitGroup{}
	wg.Add(1)
	go func() {
		defer wg.Done()
		status := <-cbChan
		assert.Equal(t, CallbackStatusOk, status)
	}()

	reqBody := &bytes.Buffer{}
	payload := callbackPayload{
		RunID: "testrunid",
		State: "ok",
	}
	err := json.NewEncoder(reqBody).Encode(payload)
	require.NoError(t, err)

	req := httptest.NewRequest("POST", cbURL, reqBody)
	w := httptest.NewRecorder()
	cbRountine.handler(w, req)

	resp := w.Result()
	assert.Equal(t, http.StatusOK, resp.StatusCode)
	wg.Wait()
}
