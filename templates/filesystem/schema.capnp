@0xfe38816f8b1419d9;

struct Schema {
    storagePool @0 :Text; # Name of the parent
    name @1 :Text; # Name of the filesystem
    sizeOnDisk @2 :UInt32; # Amount of MiB of storage used by the filesystem
    readOnly @3: Bool;
    quota @4: UInt32; # Amount of MiB that can be written to the filesystem. 0 means no quota is set.
    mountpoint @5:Text;
    status @6:Status;
}


enum Status{
    error @0;
    warning @1;
    running @2;
}