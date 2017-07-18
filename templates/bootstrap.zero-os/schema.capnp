@0x921f9bfbc5173ac9;

struct Schema {
    zerotierNetID @0 :Text;
    zerotierToken @1 :Text;
    # networks the new node needs to consume
    networks @2 :List(Text);
    wipedisks @3 :Bool=false;
    hardwarechecks @4 :List(Text);
    registrations @5 :List(Text);
}
