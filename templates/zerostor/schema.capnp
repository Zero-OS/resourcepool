@0xdeaf0f1201836a1f;

struct Schema {
    dataDir @0 :Text; # directory where the storageEngine db will be stored
    metaDir @1 :Text; # directory where the storageEngine db will be stored
    maxSizeMsg @2 :Uint8 = 32; # size of the message zerostor can accept, in Mib

    bind @3: Text; # listen bind address.

    container @4 :Text; # pointer to the parent service
    status @5: Status;

    enum Status{
        halted @0;
        running @1;
        halting @2;
    }
}
