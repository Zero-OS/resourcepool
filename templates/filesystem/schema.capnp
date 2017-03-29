@0xfe38816f8b1419d9;

struct Schema {
    storagePool @0 :Text; # Name of the parent
    sizeOnDisk @1 :UInt32; # Amount of MiB of storage used by the filesystem
    readOnly @2: Bool;
    quota @3: UInt32; # Amount of MiB that can be written to the filesystem. 0 means no quota is set.
    mountpoint @4:Text;
}
