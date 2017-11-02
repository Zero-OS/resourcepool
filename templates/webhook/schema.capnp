@0xba1b287b79988eae; 

struct Schema {
    url @0: Text;
    eventtypes @1:List(EventType); # list of eventtypes this webhook is registered to.

    enum EventType {
        ork @0;
    }

}
