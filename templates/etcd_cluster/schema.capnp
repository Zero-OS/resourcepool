@0xdc031d387f8ba074;

struct Schema {
    etcds @0: List(Text);
    status @1: Status;

    enum Status{
        halted @0;
        running @1;
    }
}
