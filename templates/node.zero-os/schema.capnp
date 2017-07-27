@0xe57bd212ca5bb013;

struct Schema {
    id @0: Text; # mac address of the mngt network card
    status @1: NodeStatus;
    hostname @2: Text;

    networks @3:List(Text); # list of consumed network config

    redisAddr @4 :Text; # redis addr for client
    redisPort @5 :UInt32 = 6379; # redis port for client
    redisPassword @6 :Text; # redis password for client
    healthchecks @7 :List(HealthCheck);

    enum NodeStatus {
        running @0;
        halted @1;
    }

    struct HealthCheck {
      id @0: Text;
      name @1: Text;
      resource @2: Text;
      messages @3: List(Message);
      category @4: Text;
      lasttime @5: Float32;
      interval @6: Float32;
      stacktrace @7: Text;
    }

    struct Message {
      id @0: Text;
      status @1: Text;
      text @2: Text;
    }
}
