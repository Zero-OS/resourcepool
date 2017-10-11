@0xb09f7b68763082a3;

struct Schema {
    label @0 :Text;
    status @1 :Status = empty;
    nrServer @2 :UInt32 = 256;
    diskType @3:DiskClass = ssd;
    filesystems @4:List(Text);
    storageServers @5 :List(Text);

    nodes @6 :List(Text);  # list of node where we can deploy storage server

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
