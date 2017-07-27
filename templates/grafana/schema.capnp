@0xfa844e8aee1ee5f2; 

struct Schema {
    node @0 :Text; # Pointer to the parent service
    influxdb @1 :List(Text); # influx db to connect to
    port @2 : UInt32 = 3000; # port
    url @3 : Text = ""; # The front facing path of the server, can use placeholders from grafana config, eg. %(protocol)s://%(domain)s:%(http_port)s/grafana/12316546
    container @4 : Text; # Container spawned by this service
    status @5 :Status;

    enum Status{
        halted @0;
        running @1;
    }
}
