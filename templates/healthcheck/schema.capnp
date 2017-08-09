@0x99e925b6b30fbe10;

struct Schema {
    healthchecks @0 :List(HealthCheck);

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
