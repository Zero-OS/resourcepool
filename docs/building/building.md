# Building the Resource Pool API Server

```
git clone https://github.com/g8os/resourcepool
cd grid/api
go build
```

If you want to compile a fully static binary use:
```
CGO_ENABLED=0
GOOS=linux
go build -a -ldflags '-extldflags "-static"' .
```

See [Starting AYS, the API Server and the bootstrap service](/docs/setup/dev.md#start-services) on how to use the `g8os_grid_installer82.sh` script from [Jumpscale/developer](https://github.com/Jumpscale/developer) to build and run the API server in a JumpScale 8.2 development Docker container.
