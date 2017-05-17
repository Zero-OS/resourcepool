# Running the Resource Pool API Server

```
./api --bind :8080 --ays-url http://aysserver.com:5000 --ays-repo grid
```

`--bind` specifies the `address:port` on which the server will listen on all interfaces, in the above example port `8080` on `localhost`
`--ays-url` specifies the `address:port` of the AYS REST API, in the above example `http://aysserver.com:5000`
`--ays-repo` specifies the name of the AYS repository the resource pool API needs to use, in the above example `grid`

See [Starting AYS, the API Server and the bootstrap service](/docs/setup/dev.md#start-services) on how to use the `g8os_grid_installer82.sh` script from [Jumpscale/developer](https://github.com/Jumpscale/developer) to build and run the API server in a JumpScale 8.2 development Docker container.
