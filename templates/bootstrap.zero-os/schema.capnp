@0xf98e6c38e1b8df58;

struct Schema {
    zerotierNetID @0 :Text;
    zerotierToken @1 :Text;
    networks @2 :List(Text);
    wipedisks @3 :Bool=false;
    # networks the new node needs to consume
}
