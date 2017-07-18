@0xdc031d387f8ba074;

struct Schema {
    etcds @0: List(Text);
    nodes @1 :List(Text); # list of node where we can deploy etcd servers
    size @2: UInt8; # Size of the cluster should be 1, 3, 5
    status @3: Status;

    enum Status{
        halted @0;
        running @1;
    }
}
