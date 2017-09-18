@0xfe38816f8b1419d9;

struct Schema {
    storagePool @0 :Text; # Name of the parent
    name @1 :Text; # Name of the filesystem
    sizeOnDisk @2 :UInt32; # Amount of MiB of storage used by the filesystem
    readOnly @3: Bool;
    quota @4: UInt32; # Amount of MiB that can be written to the filesystem. 0 means no quota is set.
    mountpoint @5:Text;
    status @6:Satus;
}


enum Status{
    error @1;
    warning @2;
    running @3;
}