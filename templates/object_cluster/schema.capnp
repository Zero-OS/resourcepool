@0x8ebb5df427f8e71c;

struct Schema {
    label @0 :Text;
    status @1 :Status = empty;
    nrServer @2 :UInt32 = 256;
    dataDiskType @3:DiskClass = hdd;
    metaDiskType @4:DiskClass = ssd;
    serversPerMetaDrive @5:UInt32;
    filesystems @6:List(Text);
    zerostors @7 :List(Text);

    nodes @8 :List(Text); # list of node where we can deploy storage server

    dataShards @9:UInt32;
    parityShards @10:UInt32;

    zerostorOrganization @11:Text;
    zerostorNamespace @12:Text;
    zerostorClientID @13:Text;
    zerostorSecret @14:Text;

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
