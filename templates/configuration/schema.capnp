@0x8e103b5cd3095968;

struct Schema {
    configurations @0: List(Conf); # List of configurations

    struct Conf {
        key @0 :Text; # Name of the configuration
        value @1 :Text; # Value of the configuration
    }
}