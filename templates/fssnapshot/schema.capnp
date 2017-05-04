@0xd8dffde6e8174b32;

struct Schema {
    filesystem @0 :Text; # Name of the parent
    name @1 : Text; # Name of the snapshot
    path @2 : Text;
    sizeOnDisk @3 : UInt32; # Amount of MiB of storage used by the filesystem
    timestamp @4 : UInt32; # Creation timestamp
}
