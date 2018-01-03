@0xe94696d8e021e01d;

struct Schema {
    zerotierNetID @0 :Text;
    zerotierToken @1 :Text;
    # networks the new node needs to consume
    networks @2 :List(Text);
    wipedisks @3 :Bool=false;
    hardwarechecks @4 :List(Text);
    registrations @5 :List(Text);
    authorizedZerotierMembers @6 : List(Text);
}
