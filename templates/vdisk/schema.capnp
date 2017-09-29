@0xb238d2ae3aa01ee0;

struct Schema {
    size @0 :UInt64;
    blocksize @1 :UInt32;
    type @2 :VdiskType;
    templateVdisk @3 :Text; # in case it's a copy of another vdisk
    readOnly @4 :Bool;
    status @5 :Status;
    vdiskstorage @6 :Text;
    timestamp @7: UInt64;
    templateStorageCluster @8 :Text;
    backupUrl @9 :Text;
    enum Status {
        halted @0;
        running @1;
        rollingback @2;
        orphan @3;
    }

    enum VdiskType {
        boot @0;
        db @1;
        cache @2;
        tmp @3;
    }
}
