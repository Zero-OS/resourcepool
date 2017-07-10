from termcolor import colored
from random import randint
from install_testing_nodes.src.ExecuteRemoteCommands import ExecuteRemoteCommands
from install_testing_nodes.src.install_g8os_on_packet import InstallG8OSOnPacket

MACHINE_PLAN = 'baremetal_0'  # Type 1
ZEROTIER_NW_ID = None
MACHINES_NUMBER = 1
AUTO_DISCOVERING = True

JUMPSACLE_BRANCH = "master"
RELEASE_VERSION = "master"
AYS_TEMPLATE_BRANCH = RELEASE_VERSION
GRID_API_BRANCH = RELEASE_VERSION
G8CORE_CLIENT = RELEASE_VERSION
IPXE_SCRIPT = 'https://bootstrap.gig.tech/ipxe/{}/{}/debug'.format(RELEASE_VERSION, {})

MACHINES = []

if __name__ == '__main__':
    install_g8os_on_packet = InstallG8OSOnPacket()
    executer = ExecuteRemoteCommands()
    print(colored(' [*] STEP 1 : Create new zerotier network ... ', 'white'))
    executer.create_zerotire_nw(use_this_nw=ZEROTIER_NW_ID)
    print(colored(' [*] STEP 2 : Install g8os in packet, image: %s' % IPXE_SCRIPT, 'yellow'))
    for i in range(MACHINES_NUMBER):
        MACHINE_NAME = 'Test-xtremx-0%i' % randint(1, 1000)
        MACHINES.append(install_g8os_on_packet.create_new_device(hostname=MACHINE_NAME,
                                                                 plan=MACHINE_PLAN,
                                                                 ipxe_script_url=IPXE_SCRIPT))
    print(colored(' [*] STEP 3 : create account', 'yellow'))
    executer.create_account()
    print(colored(' [*] STEP 4 : create cloud space', 'yellow'))
    executer.create_cloudspace()

    # if not AUTO_DISCOVERING:
    #     MACHINE_IP = install_g8os_on_packet.get_packt_machine_ip(machine_name=MACHINE_NAME)
    #     MACHINE_MAC = install_g8os_on_packet.get_packet_machine_mac(ip=MACHINE_IP)
    #     executer.update_g8os_valuse(MACHINE_IP, MACHINE_MAC)

    # AYS server vm
    print(colored(' [*] STEP 5 : create AYS server node', 'yellow'))
    executer.create_virtualmachine()
    executer.create_port_forward(publicPorts={22: 2201, 5000: 5000})
    executer.connect_to_virtual_machine(port=2201)
    executer.update_machine()
    executer.add_ssh_key()
    executer.install_zerotire()
    executer.add_node_to_zerotire_nw()
    executer.authorize_zerotire_member(member=executer.get_zerotire_info())
    executer.install_jumpscale(branch=JUMPSACLE_BRANCH)
    executer.install_zerotire_lib()
    executer.install_orchestrator_python_client(branch=G8CORE_CLIENT)
    executer.start_AYS_server()
    executer.clone_ays_templates(branch=AYS_TEMPLATE_BRANCH)
    executer.discover_g8os_nodes(auto_discovering=True)
    executer.get_virtualmachine_ip()
    ays_server_ip = executer.virtualmachine['ip']

    # grid API node
    print(colored(' [*] STEP 6 : create grid API server', 'yellow'))
    executer.create_virtualmachine()
    executer.create_port_forward(publicPorts={22: 2202, 8080: 8080})
    executer.connect_to_virtual_machine(port=2202)
    executer.update_machine()
    executer.add_ssh_key()
    executer.install_zerotire()
    executer.add_node_to_zerotire_nw()
    executer.authorize_zerotire_member(member=executer.get_zerotire_info())
    executer.install_go()
    executer.start_API_server(API_branch=GRID_API_BRANCH,
                              ays_server_ip=ays_server_ip)
    executer.get_virtualmachine_ip()
    print('\n')
    print(colored(' [*] http://%s:8080' % executer.cloudspace['ip'], 'cyan'))
