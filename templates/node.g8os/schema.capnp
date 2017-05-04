@0xdde10a317425c8d3;

struct Schema {
    id @0: Text; # mac address of the mngt network card
    status @1: NodeStatus;
    hostname @2: Text;

    networks @3:List(Text); # list of consumed network config

    redisAddr @4 :Text; # redis addr for client
    redisPort @5 :UInt32 = 6379; # redis port for client
    redisPassword @6 :Text; # redis password for client

    enum NodeStatus {
        running @0;
        halted @1;
    }
}
