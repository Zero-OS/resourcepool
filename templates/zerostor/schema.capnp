@0xf638885fb1e0164f;

struct Schema {
    dataDir @0 :Text; # directory where the storageEngine db will be stored
    metaDir @1 :Text; # directory where the storageEngine db will be stored

    bind @2: Text; # listen bind address.

    container @3 :Text; # pointer to the parent service
    status @4: Status;

    enum Status{
        halted @0;
        running @1;
        halting @2;
    }
}
