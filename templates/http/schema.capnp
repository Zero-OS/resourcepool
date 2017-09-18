@0xed032b71b39fc494;

struct Schema {
    container @0 :Text; # pointer to the parent service
    type @1 :Scheme; # what type of proxy to configure

    enum Scheme {
        http @0;
        https @1;
    }
}
