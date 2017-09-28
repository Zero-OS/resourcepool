@0xaaa9694b64fdd6fa;

struct Schema {
    ftpURL @0 :String; # FTP server url of the image you want to import
    size @1 :UInt64;
    blocksize @2 :UInt32;
    vdiskstorage @3 :Text; # parent
    exportName @4 :String
    exportSnapshot @5 :String
}