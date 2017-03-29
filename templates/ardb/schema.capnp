@0x935023b5e21bf041;

struct Schema {
    homeDir @0 :Text; # directory where the ardb db will be stored
    bind @1: Text; # listen bind address.

    master @2 :Text;
    # name of other ardb service that needs to be used as master
    # if this is filled, this instance will behave as a slave

    container @3 :Text; # pointer to the parent service
}
