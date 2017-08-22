@0xdc031d387f8ba074;

struct Schema {
    etcds @0: List(Text);
    status @1: Status;
    nodes @2 :List(Text); # list of node where we can deploy etcd servers

    enum Status{
        halted @0;
        running @1;
        recovering @2;
    }
}
