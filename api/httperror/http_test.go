package httperror

import (
	"net/http"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestHTTPError(t *testing.T) {
	resp := &http.Response{
		StatusCode: http.StatusInternalServerError,
	}
	err := New(resp, "this is an %s", "error")
	assert.Equal(t, err.Error(), "this is an error")
	assert.NotNil(t, err.Resp)
	assert.Equal(t, err.Resp.StatusCode, http.StatusInternalServerError)
}
