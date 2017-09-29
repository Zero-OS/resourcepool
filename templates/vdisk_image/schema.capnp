@0xf355af400c5e02c5;

struct Schema {
    ftpURL @0 :Text; # FTP server url of the image you want to import
    size @1 :UInt64;
    imageBlockSize @2 :UInt32=131072;
    diskBlockSize @3 :UInt32=4096;
    vdiskstorage @4 :Text; # parent
    exportName @5 :Text;
    exportSnapshot @6 :Text;
    encryptionKey @7 :Text;
}