@0x9e47335012092925;

struct Schema {
    id @0 :Text;
    apiURL @1 :Text;
    # URL of the grid API, this is used by nbdservers to know where to
    # get information about the storage cluster and vdisks
}
