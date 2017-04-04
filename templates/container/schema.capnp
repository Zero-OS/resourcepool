@0x935023b5e21ba041;

struct Schema {
    node @0 :Text; # pointer to the parent service
    status @1 :Status;
    hostname @2 :Text;
    flist @3 :Text; # Url to the root filesystem flist
    initProcesses @4 :List(Process);
    filesystems @5 :List(Text); # pointer to the filesystem to mount into the container
    zerotier @6 :Text; # pointer to the zerotier service to consume
    bridges @7 :List(Text); # pointers to the bridges to consumes
    hostNetworking @8 :Bool;
    # Make host networking available to the guest.
    # If true means that the container will be able participate in the networks available in the host operating system.
    ports @9:List(Text); # List of node to container post mappings. e.g: 8080:80
    storage @10 :Text;
    id @11: UInt32;
    mounts @12: List(Mount); # List mount points mapping to the container
    enum Status{
        running @0;
        halted @1;
    }

    struct Mount {
        filesystem @0 :Text; # Instance name of a filesystem service
        target @1 :Text; # where to mount this filesystem in the container
    }

    struct Process {
        name @0 :Text; # Name of the executable that needs to be run
        pwd @1 :Text; # Directory in which the process needs to be started
        args @2 :List(Text); #  List of commandline arguments
        environment @3 :List(Text);
        # Environment variables for the process.
        # e.g:  'PATH=/usr/bin/local'
        stdin @4 :Text; # Data that needs to be passed into the stdin of the started process
    }
}
