@0xf5773e7b7181182f;

struct Schema {
    size @0 :UInt64;
    blocksize @1 :UInt32;
    deduped @2 :Bool;
    templateVolume @3 :Text; # in case it's a copy of another volume
    readOnly @4 :Bool;
    driver @5 :Text;
    status @6 :Status;
    gridApiUrl @7:Text;
    node @8 :Text;
    containerId @9 :UInt32;

    storageCluster @10 :Text; # parent

    enum Status {
        running @0;
        halted @1;
        rollingback @2;
    }
}
