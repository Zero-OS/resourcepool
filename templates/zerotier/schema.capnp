@0xb755efbee1c680d0;

struct Schema {
    nwid @0 :Text;
    node @1 :Text; # parent
    allowDefault @2 :Bool;
    allowGlobal @3 :Bool;
    allowManaged @4 :Bool;
    assignedAddresses @5 :List(Text);
    bridge @6 :Bool;
    broadcastEnabled @7 :Bool;
    mac @8 :Text;
    mtu @9 :UInt64;
    name @10 :Text;
    netconfRevision @11 :UInt64;
    portDeviceName @12 :Text;
    portError @13 :UInt64;
    routes @14 :List(Route);
    status @15 :Text;
    type @16 :Type;
    dhcp @17 :Bool;

}

struct Route {
    flags @0 :UInt64;
    metric @1 :UInt64;
    target @2 :Text;
    via @3 :Text;
}

enum Type {
    private @0;
    public @1;
}