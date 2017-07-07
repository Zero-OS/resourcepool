# feedback machanism Z-OS

## intro

- ays service can ask Z-OS to launch a container or a vm
- ays service can ask Z-OS to launch one or more processes in a container
- ays service can ask Z-OS to launch zerotier network on container or vm

## error conditions

- std error on process in container
- processes in container stops (exit 0 or 0+ return code)
    - STDERR: 'HALT 0', 'HALT 1', ...
- vm stops (can this be detected?)
    - STDERR: 'HALT VM'
- process/vm uses too much CPU
    - STDERR: 'CPU_OVERLOAD_PERC $percentOver5min'
    - is checked by polling local redis aggregated info (so no need to aggregate in golang)
- vm has too many context switches
    - STDERR: 'CPU_OVERLOAD_CS $avgamount5min'
    - is checked by polling local redis aggregated info (so no need to aggregate in golang)
- 1 of nics of vm uses too much bandwidth or too many open connections or other wrong network situations...
    - STDERR: 'NIC_OVERLOAD_????'
    - is checked by polling local redis aggregated info (so no need to aggregate in golang)
- zerotier network down
    - complete...
- COMPLETE...

## feedback

- stdout from process in container

## when launching container or vm or zerotier (through redis cmd channel)

- specify name/instance of ays service
- the Core0
    - tracks stdout/stderr and other errorconditions mentioned above
    - sends the stdout to orchestrator on url
        - /stdout/$actorname/$serviceinstancename
        - /stderr/$actorname/$serviceinstancename
    - send as json?
    - params of json
        - process name if relevant
        - data (text of stdout/stderr)
        - ???
- orchestrator (AYS service)
    - gives info of json to predefined method on AYS instance
    - method
        - stdout (processname,output,...)
        - stderr (processname,errortxt,...)
    - these are pre-defined methods and only when filled in will be used

remarks
- best would be this is core functionality of Z-OS and not a separate daemon

## alternative

- this approach has following disadvantages
    - core0 needs to know about orchestrator, this makes it more stateful and I think more messy.
    - performance +-, lots of load on orchestrator, this could lead to denial of service
- why not use logger to redis functionality
    - need to document what we have (so we know what to change)
    - need see how to send stderr/stdout per process/vm to redis
    - redis needs to remove too old logs (rolling logs of stdout)
    - why not use https://redis.io/topics/pubsub to announce changes (not the actual content but pointers to new info on well defined channels)
    - each stdout/err message needs to be timestamped
