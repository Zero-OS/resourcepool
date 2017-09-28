

## 0-Orchestrator Testsuite
- Here is the link for the tests: [testsuite](api_testing/testcases)

### 1- Running using Travis
- When travis triggers the python environment, Basically it starts to create number of packet machines  using specific images that matches the branch you are running from, then run the tests on it.
- After the tests are done, packet machines is deleted.

#### How Travis works?
- For this Project, travis is configured to start a matrix to run two different jobs, each using a different environment

-  One environment is using go while the other is using python. Both of them will always be triggered with each commit 
   but the python environment will never run the tests unless the trigger is caused due to cron jobs or manually (using api). So for instance if a job has been triggered due to a pull request, the python environment will be created but soon it will be terminated as there are no tests to run.


#### Trigger Manual builds

##### To trigger a manual build using travis, use one of the following ways:

1- Travis Dashboard
- Go to [travis-beta-features](https://travis-ci.org/features), and enable the the Dashboard option then a click on the Travis CI logo at the top gets you there!
- Once you are there, you can trigger a manual build as shown in figure. This build is triggered from the default branch
![](pics/dashboard-repo.png)

2- CI-dashboard tool
- Please find all needed steps [here](https://github.com/ahmedelsayed-93/ci-dashboard) to launch your dashboard.
- The nice about this tool that it can give you all Travis Dashboard options plus some nice options. For instance you can trigger the build from any branch. 
- Also it gives you a nicer clear view of the status of your repos.
   
3- trigger_travis.sh script
- The advantage of this script is that the build can be triggered from any branch. Here is the script [trigger_travis](trigger_travis.sh)
- For this script to work, a travis token need to be provided. To generate token, you need to install line command travis client [travis-client](https://github.com/travis-ci/travis.rb#installation), then use these commands:
    ```
    travis login --org
    travis token --org
    ```
- For instance, to trigger a build from master branch, the branch "master" and the token should be passed to the script
    ```
    bash trigger_travis.sh master l17-fmjUgycEAcQWWCA
    ```

### 2- Running Manually 

#### Clone this repo 
```bash
git clone https://github.com/zero-os/0-orchestrator.git
```
#### Install requirements
```bash
cd 0-orchestrator/tests/Grid_API_Testing/
pip3 install -r requirements.txt
```
#### Set your configrations
```ini
[main]
api_base_url = #the url of the Zero-OS Cluste
zerotier_token = #zerotier account token
client_id = #itsyouonline account client id
client_secret = #itsyouonline account client secret
organization = #itsyouonline organization

```
> [See how to setup a Zero-OS Cluste](https://github.com/zero-os/0-orchestrator/tree/master/docs/setup)


#### Run tests
```bash
cd 0-orchestrator/tests/Grid_API_Testing/
export PYTHONPATH=./
nosetests -s -v api_testing/testcases --tc-file api_testing/config.ini
```
### 3- Running in be-scale-2

- Update booting image with zero-os ipxi url  in the following file : 
```/opt/g8-pxeboot/pxeboot/tftpboot/pxelinux.cfg/911boot```
Example :
```
    DEFAULT G8OS-lkrn
    TIMEOUT 100
    PROMPT  1
    IPAPPEND 2
    label G8OS-lkrn
            kernel ipxe.lkrn
            append dhcp && chain https://bootstrap.gig.tech/ipxe/zero-os-master/{zerotiernetwork_id}/organization={organization_name}%20pcie_aspm=off
```
- boot Cpu nodes with Zero-os ipxi using IPMI tool : 
  - get IMPI ips for cpus from ```/opt/g8-pxeboot/pxeboot/conf/hosts ```
  - Use IPMI tool to boot node like this :
  ```ipmitool -I lanplus -H "cpu_ipmi_ip" -U ADMIN -P ADMIN chassis bootdev pxe```
  -  Use IPMI tool to restart node like this :
  ```ipmitool -I lanplus -H "cpu_ipmi_ip" -U ADMIN -P ADMIN chassis power cycle```

***note: you can install orchestrator server in js9 docker in controller***

### Setup the backplane network in be-scale-2

##### G8 setup

```
network.zero-os-bond__storage:
  vlanTag: 2313
  cidr: "10.105.3.0/24"
  driver: ixgbe
```


