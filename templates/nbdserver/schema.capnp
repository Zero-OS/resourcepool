@0xf6773e7b7181183f;

struct Schema {
    backendControllerUrl @0 :Text;
    volumeControllerUrl @1 :Text;
    socketPath @2 :Text; # uri of the unix socket path
    container @3 :Text; # parent
}
