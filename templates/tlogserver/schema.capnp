@0xe97fdbcd2e47a6cd;

struct Schema {
    container @0 :Text; # parent
    bind @1 :Text; # parent
    status @2: Status;
    waitListenBind @3: Text;
    acceptAddress @4: Text;


    enum Status{
        halted @0;
        running @1;
        halting @2;
    }

}
