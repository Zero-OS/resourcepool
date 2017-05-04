@0x80eab0d1fa3f13a4;

struct Schema {
    label @0 :Text;
    status @1 :Status = empty;
    nrServer @2 :UInt32 = 256;
    hasSlave @3 :Bool = false;
    diskType @4:DiskClass = ssd;
    filesystems @5:List(Text);
    ardbs @6 :List(Text);

    nodes @7 :List(Text); # list of node where we can deploy storage server

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
