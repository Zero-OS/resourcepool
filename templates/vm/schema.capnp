@0x9f953e9e7f5493cf;

struct Schema {
    node @0: Text; # pointer to the parent service
    status @1: Status;
    id @2: Text;
    memory @3: UInt16; # Amount of memory in MiB
    cpu @4: UInt16; # Number of virtual CPUs
    nics @5: List(NicLink);
    disks @6: List(DiskLink);
    vdisks @7: List(Text); # consume vdisk services, should not be set via blueprint, will be calculated from disks
    vnc @8: Int32 = -1; # the vnc port the machine is listening to
    backupUrl @9 :Text; # Used for export vm, ghost property, should be removed after passing args is supported
    cryptoKey @10 :Text; # Used for export vm, ghost property, should be removed after passing args is supported
    exportPath @11 :Text; # Used for export vm, ghost property, should be removed after passing args is supported

    enum Status{
        deploying @0;
        error @1;
        halted @2;
        running @3;
        paused @4;
        halting @5;
        migrating @6;
        starting @7;
        networkKilled @8;
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
      bridge @3;
    }

}
