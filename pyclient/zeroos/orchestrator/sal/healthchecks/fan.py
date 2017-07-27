from ..healthcheck import HealthCheckRun
descr = """
Checks the fans of a node using IPMItool.
Result will be shown in the "Hardware" section of the Grid Portal / Status Overview / Node Status page.
"""

class Fan(HealthCheckRun):
    def __init__(self, node):
        resource = '/nodes/{}'.format(node.name)
        super().__init__(id='FAN', name="Fan", category="Hardware", resource=resource)

    def run(self, container):
        out = container.client.bash("""ipmitool sdr type "Fan" """).get()
        if out.state.upper() != "ERROR":
            out = out.stdout
            if out:
                # SAMPLE:
                # root@du-conv-3-01:~# ipmitool sdr type "Fan"
                # FAN1             | 41h | ok  | 29.1 | 5000 RPM
                # FAN2             | 42h | ns  | 29.2 | No Reading
                # FAN3             | 43h | ok  | 29.3 | 4800 RPM
                # FAN4             | 44h | ns  | 29.4 | No Reading

                for line in out.splitlines():
                    parts = [part.strip() for part in line.split("|")]
                    id_, sensorstatus, text = parts[0], parts[2], parts[-1]
                    if sensorstatus == "ns" and "no reading" in text.lower():
                        self.add_message(id=id_, status='SKIPPED', text="Fan {id} has no reading ({text})".format(id=id_, text=text))
                    elif sensorstatus != "ok" and "no reading" not in text.lower():
                        self.add_message(id=id_, status='WARNING', text="Fan {id} has problem ({text})".format(id=id_, text=text))
                    elif sensorstatus == 'ok':
                        self.add_message(id=id_, status="OK", text="Fan {id} is working at ({text})".format(id=id_, text=text))
            else:
                self.add_message(id="SKIPPED", status="SKIPPED", text="NO fan information available")
        else:
            self.add_message(id="ERROR", status="ERROR", text="ERROR getting fan information")
