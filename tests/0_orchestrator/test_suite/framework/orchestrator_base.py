import uuid, random, requests


class OrchestratorBase:
    def random_string(self, size=10):
        return str(uuid.uuid4()).replace('-', '')[:size]

    def update_default_data(self, default_data, new_data):
        for key in new_data:
            default_data[key] = new_data[key]
        return default_data

    def randomMAC(self):
        random_mac = [0x00, 0x16, 0x3e, random.randint(0x00, 0x7f), random.randint(0x00, 0xff),
                      random.randint(0x00, 0xff)]
        mac_address = ':'.join(map(lambda x: "%02x" % x, random_mac))
        return mac_address

    def random_choise(self, data):
        return random.choice(data)

