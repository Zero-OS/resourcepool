@0xaf827ecce8244a14;

struct Schema {
    label @0 :Text;
    status @1 :Status = empty;
    nrServer @2 :UInt32 = 256;
    diskType @3:DiskClass = ssd;
    metadiskType @4:DiskClass = ssd;
    filesystems @5:List(Text);
    storageEngines @6 :List(Text);

    nodes @7 :List(Text); # list of node where we can deploy storage server

    clusterType @8 :Type = block;
    dataShards @9: UInt32;
    parityShards @10: UInt32;

    enum Type {
        block @0;
        object @1;
    }

    enum Status{
        empty @0;
        deploying @1;
        ready @2;
        error @3;
    }

    enum DiskClass {
        nvme @0;
        ssd @1;
        hdd @2;
        archive @3;
    }
}
