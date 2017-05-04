@0xdab765cd6c357ea4;

struct Schema {
    zerotierNetID @0 :Text;
    zerotierToken @1 :Text;

    networks @2 :List(Text);
    # networks the new node needs to consume
}
