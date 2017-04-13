@0xf5773e7b7181183f;

struct Schema {
    size @0 :UInt64;
    blocksize @1 :UInt32;
    type @2 :VolumeType;
    templateVolume @3 :Text; # in case it's a copy of another volume
    readOnly @4 :Bool;
    status @5 :Status;

    storageCluster @6 :Text; # consume
    tlogStoragecluster @7 :Text; # consume

    enum Status {
        halted @0;
        running @1;
        rollingback @2;
    }

    enum VolumeType {
        boot @0;
        db @1;
        cache @2;
        tmp @3;
    }
}
