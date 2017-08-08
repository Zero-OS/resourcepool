@0xb61762c35585eed8;

struct Schema {
    node @0 :Text; # pointer to the parent service
    port @1 :UInt16;
    status @2 :Status;
    enum Status {
        opened @0;
        dropped @1;
    }
}
