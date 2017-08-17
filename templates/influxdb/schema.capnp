@0xc75c2e3ade4b6c71;

struct Schema {
    node @0 :Text; # Pointer to the parent service
    port @1 :UInt32 = 8086; # port to connect to influxdb
    rpcport @2 :UInt32 = 8088; # RPC port for backup and restore
    databases @3: List(Text); # database to dump statistics to
    container @4 :Text; # Container spawned by this service
    status @5 :Status;

    enum Status{
        halted @0;
        running @1;
    }
}
