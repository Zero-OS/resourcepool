
## How to build
```shell
git clone https://github.com/zero-os/0-orchestrator
cd grid/api
go build
```

If you want to compile a fully static binary use :
`CGO_ENABLED=0 GOOS=linux go build -a -ldflags '-extldflags "-static"' .`

## How to run

`./api --bind :8080 --ays-url http://aysserver.com:5000 --ays-repo grid`
- `--bind :8080` makes the server listen on all interfaces on port 8080
- `--ays-url` need to point to the AYS REST API
- `--ays-repo` is the name of the AYS repository the Grid API need to use
