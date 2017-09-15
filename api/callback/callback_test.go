package callback

import (
	"bytes"
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestCallBack(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()
	cbHandler := NewCallbackRoutine(ctx)

	runid := "testrunid"
	cbChan := cbHandler.Wait(runid)

	go func() {
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

	req := httptest.NewRequest("POST", "http://example.com/foo", reqBody)
	w := httptest.NewRecorder()
	cbHandler.Handler(w, req)

	resp := w.Result()
	assert.Equal(t, http.StatusOK, resp.StatusCode)
}
