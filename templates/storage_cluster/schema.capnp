@0xd2006eaa1b96f733;

struct Schema {
    label @0 :Text;
    status @1 :Status = empty;
    nrServer @2 :UInt32 = 256;
    diskType @3:DiskClass = ssd;
    metadiskType @4:DiskClass = ssd;
    serversPerMetaDrive @5:UInt32;
    filesystems @6:List(Text);
    storageEngines @7 :List(Text);

    nodes @8 :List(Text); # list of node where we can deploy storage server

    clusterType @9 :Type = block;
    dataShards @10: UInt32;
    parityShards @11: UInt32;

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
