# Running the Zero-OS Orchestrator

```
./api --bind :8080 --ays-url http://aysserver.com:5000 --ays-repo grid
```

- `--bind` specifies the `address:port` on which the server will listen on all interfaces, in the above example port `8080` on `localhost`
- `--ays-url` specifies the `address:port` of the AYS RESTful API, in the above example `http://aysserver.com:5000`
- `--ays-repo` specifies the name of the AYS repository the 0 Rest Zero-OS Orchestrator needs to use, in the above example `grid`
- `--ays-retries` configures the ays run retries behavior. If not supplied, the default ays retries behavior is used.
    the value supplied should contain comma-separated integers where the index of the integer is the number of the retry and the value
    of the integer is the delay between this run and the previous one.
    
    Examples:
    - --ays-retries 2,4,6 : this will configure the run to have 3 retries, first retry is 2 seconds after the first run, 2nd retry is 4 seconds after the 1st retry and 3rd retry is 6 seconds after the 2nd retry.
    - --ays-retries 0 : this will configure the runs to have no retries.


See [Starting AYS, the API Server and the bootstrap service](/docs/setup/setup.README.md#start-services) on how to use the `g8os_grid_installer82.sh` script from [Jumpscale/developer](https://github.com/Jumpscale/developer) to build and run the API server in a JumpScale 8.2 development Docker container.
