@0x8fb9cec5b1fd4b11;

struct Schema {
    hwaddr @0 :Text; # Macaddress for the bridge to be created. If none, a random macaddress will be assigned
    networkMode @1 :NetworkMode;
    nat @2 :Bool;  # If true, SNAT will be enabled on this bridge.
    setting @3: Setting;
    status @4: Status;
    node @5: Text; # pointer to parent service

    enum NetworkMode{
        none @0;
        static @1;
        dnsmasq @2;
    }

    enum Status {
        up @0;
        down @1;
        error @2;
    }

    struct Setting {
    # Networking settings, depending on the selected mode.
    # none:
    #   no settings, bridge won't get any ip settings
    # static:
    #   settings={'cidr': 'ip/net'}
    #   bridge will get assigned the given IP address
    # dnsmasq:
    #   settings={'cidr': 'ip/net', 'start': 'ip', 'end': 'ip'}
    #   bridge will get assigned the ip in cidr
    #   and each running container that is attached to this IP will get
    #   IP from the start/end range. Netmask of the range is the netmask
    #   part of the provided cidr.
    #   if nat is true, SNAT rules will be automatically added in the firewall.
        cidr @0: Text;
        start @1: Text;
        end @2: Text;
    }
}
