@0xf11a2557d84276d9;

struct Schema {
    size @0 :UInt64;
    blocksize @1 :UInt32;
    type @2 :VdiskType;
    imageId @3 :Text; # in case it's a copy of another vdisk
    readOnly @4 :Bool;
    status @5 :Status;
    vdiskstorage @6 :Text;
    timestamp @7: Int64;
    backupUrl @8 :Text; # Used for import vdisk, ghost property
    cryptoKey @9 :Text; # Used for import vdisk, ghost property
    snapshotID @10 :Text; # Used for import vdisk, ghost property

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
