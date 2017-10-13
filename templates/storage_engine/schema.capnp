@0x935023b5e21bf041;

struct Schema {
    homeDir @0 :Text; # directory where the storageEngine db will be stored
    bind @1: Text; # listen bind address.

    master @2 :Text;
    # name of other storageEngine service that needs to be used as master
    # if this is filled, this instance will behave as a slave

    container @3 :Text; # pointer to the parent service
    status @4: Status;
    enabled @5: Bool;

    enum Status{
        halted @0; # halted can be changed to running, or broken
        running @1; # running can be changed to halted or broken
        broken @2; # once the engine is in broken state, there is no going back
    }
}
