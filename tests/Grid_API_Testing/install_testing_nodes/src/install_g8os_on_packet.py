from install_testing_nodes.src.Basic import Basic
from termcolor import colored
import packet


class InstallG8OSOnPacket(Basic):
    def __init__(self):
        super().__init__()
        self.project_id = self.values['packet_project_id']
        self.manager = packet.Manager(auth_token=self.values['packet_access_token'])

    def create_new_device(self, hostname, plan, ipxe_script_url):
        self.logging.info(' [*] create new machine  .. ')
        print(colored(' [*] create new machine .. ', 'white'))
        ipxe_script_url = self.add_zerotire_nw_to_image(ipxe_script_url)
        device = self.manager.create_device(project_id=self.project_id,
                                            hostname=hostname,
                                            plan=plan,
                                            operating_system='custem_ipxe',
                                            ipxe_script_url=ipxe_script_url,
                                            facility='ewr1')
        print(colored(' [*] G8os machine : %s  .. \n' % hostname, 'green'))
        return device

    def add_zerotire_nw_to_image(self, image):
        return image.format(self.ZEROTIER_NW_ID)
