@0x96f11e85b305f456;

struct Schema {
    vlanTag @0 :UInt16;
    cidr @1 :Text; # of the storage network
    driver @2 :Text; # incase the driver requires reloading
}
