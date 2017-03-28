@0xeee35f60471101a3;

struct Schema {
    vlanTag @0 :UInt8;
    bridge @1 :Text; # the name of the consumed bridge
    node @2 :Text; # parent node
}
