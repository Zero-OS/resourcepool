@0xb7b94de8a5f8b089;

struct Schema {
    dataDir @0 :Text; # directory where the storageEngine db will be stored
    metaDir @1 :Text; # directory where the storageEngine db will be stored
    maxSizeMsg @2 :UInt8 = 64; # size of the message zerostor can accept, in MiB
    bind @3: Text; # listen bind address.

    container @4 :Text; # pointer to the parent service
    status @5: Status;

    enum Status{
        halted @0;
        running @1;
        halting @2;
    }
}
