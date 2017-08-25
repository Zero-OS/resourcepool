@0xf58014a129820bc9;

struct Schema {
    peers @0: List(Text); # list of peers urls in the cluster
    container @1 :Text; # pointer to the parent service
    serverBind @2 :Text; # server listen address.
    clientBind @3 :Text; # client bind address.
    mgmtClientBind @4 :Text; # client bind address.
    status @5: Status;
    homeDir @6 :Text; # directory where the etcd db will be stored


    enum Status{
        halted @0;
        running @1;
    }
}
