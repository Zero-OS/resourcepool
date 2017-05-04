@0xb65823af76a98818;

struct Schema {
    status @0 :Status;
    totalCapacity @1:UInt64;
    freeCapacity @2:UInt64;
    metadataProfile @3 :Profile;
    dataProfile @4 :Profile;
    mountpoint @5: Text;
    devices @6: List(PartitionMap); # List of object that map a device to a partition uuid
    node @7: Text;

    struct PartitionMap {
        device @0 :Text;
        partUUID @1 :Text;
    }

    enum Status {
        healthy @0;
        degraded @1;
        error @2;
    }

    enum Profile {
        raid0 @0;
        raid1 @1;
        raid5 @2;
        raid6 @3;
        raid10 @4;
        dup @5;
        single @6;
    }
}
