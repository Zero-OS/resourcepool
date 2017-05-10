@0x9e3b2bd4c67f73e9;

struct Schema {
    node @0: Text; # pointer to the parent service
    status @1: Status;
    id @2: Text;
    memory @3: UInt16; # Amount of memory in MiB
    cpu @4: UInt16; # Number of virtual CUPs
    nics @5: List(NicLink);
    disks @6: List(DiskLink);
    vdisks @7: List(Text); # consume vdisk services, should not be set via blueprint, will be calculated from disks
    userCloudInit @8: Text;
    systemCloudInit @9: Text;

    vnc @10: Int32 = -1; # the vnc port the machine is listening to

    enum Status{
        error @0;
        halted @1;
        running @2;
        paused @3;
        halting @4;
        migrating @5;
    }

    struct NicLink {
      id @0: Text; # VxLan or VLan id
      type @1: NicType;
      macaddress @2: Text;
    }

    struct DiskLink {
      vdiskid @0: Text;
      maxIOps @1: UInt32;
    }

    enum NicType {
      default @0;
      vlan @1;
      vxlan @2;
    }

}
