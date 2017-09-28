@0xaaa9694b64fdd6fa;

struct Schema {
    ftpURL @0 :Text; # FTP server url of the image you want to import
    size @1 :UInt64;
    blocksize @2 :UInt32;
    vdiskstorage @3 :Text; # parent
    exportName @4 :Text;
    exportSnapshot @5 :Text;
}