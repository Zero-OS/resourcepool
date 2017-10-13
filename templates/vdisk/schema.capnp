@0xe3c0cb7ad515908e;

struct Schema {
    size @0 :UInt64;
    blocksize @1 :UInt32;
    type @2 :VdiskType;
    imageId @3 :Text; # in case it's a copy of another vdisk
    readOnly @4 :Bool;
    status @5 :Status;
    vdiskstorage @6 :Text;
    timestamp @7: Int64;
    backupUrl @8 :Text;

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
