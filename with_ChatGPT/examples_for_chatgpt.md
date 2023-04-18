During the experiment with ChatGPT, we provided the following examples as prompts for ChatGPT to learn KiwiSpec:

    # Here are examples code in KiwiSpec: 
    # "id.orig_h", "id.resp_h" and "orig_pkts" are the fields in Zeek log in json format for source ip, 
    # destination ip and outbound packet count.
    # In this example, the code takes two json file - a zeek log file and an ip to server mapping file,
    # creates the output of outbound destination count and packet count for every source ip reaching out 
    # an internet IP, and writes the result to a file.

    READ  server.json AS srv, conn.json AS flows
    CREATE [{"server": s_srv, "outbound_count": ip_c, "total_pkts": pkts}] AS r
    VAR i SELECT 
        srv[flows[i]["id.orig_h"]][_] AS s_srv;  
        COUNT DISTINCT(flows[i]["id.resp_h"]) AS ip_c;
        SUM(flows[i]["orig_pkts"]) AS pkts;
    WHERE is_internet_ip(flows[i]["id.resp_h"])
    WRITE server_access_internet_cnt.json FROM r

    

    # Discovery-Network Service Scanning, this example collects all the destination host, and all the destination port,
    # and count the distinct destination host and count the distinct destination port, 
    # sort and limit 10 destination port for r1 as result and sort and limit 10 destination host for r2 as result
    # the results are written to two files.

    read conn.json AS flows
    CREATE [{"source": source, "dport":dport, "dport_c":dport_c}] AS r1 ;
        [{"source": source, "dhost": dhost, "dhost_c": dhost_c}] AS r2  
    VAR i SELECT
        flows[i]["id.orig_h"] as source;
        COLLECT SET(flows[i]["id.resp_h"]) as dhost;
        COLLECT SET(flows[i]["id.resp_p"]) as dport;
        COUNT DISTINCT(flows[i]["id.resp_h"]) as dhost_c;
        COUNT DISTINCT(flows[i]["id.resp_p"]) as dport_c;
        where flows[i]["local_orig" | True] and flows[i]["local_resp" | True];    
        flows[i]["conn_state"] in ["S0", "REJ"];
        ORDER BY dhost_c DESC LIMIT 10 FOR r2;  dport_c DESC LIMIT 10 FOR r1
    write top_sender_dport.json from r1, 
        top_sender_dhost.json from r2
   
        

    # Discovery-Network Service Scanning, this example collects all the destination host, and all the destination port,
    # and count the distinct destination host and count the distinct destination port, 
    # sort and limit 10 destination port for r1 as result and sort and limit 10 destination host for r2 as result
    # using an ip to server mapping file - server.json to update r1 and r2 to add 
    # application server name to the result structures.
    # the results are written to two files.

    read server.json AS srv_names, conn.json AS flows
    CREATE [{"source": source, "dport":dport, "dport_c":dport_c}] AS r1 ;
        [{"source": source, "dhost": dhost, "dhost_c": dhost_c}] AS r2  
    VAR i SELECT
        flows[i]["id.orig_h"] as source;
        COLLECT SET(flows[i]["id.resp_h"]) as dhost;
        COLLECT SET(flows[i]["id.resp_p"]) as dport;
        COUNT DISTINCT(flows[i]["id.resp_h"]) as dhost_c;
        COUNT DISTINCT(flows[i]["id.resp_p"]) as dport_c;
        where flows[i]["local_orig" | True] and flows[i]["local_resp" | True];    
        flows[i]["conn_state"] in ["S0", "REJ"];
        ORDER BY dhost_c DESC LIMIT 10 FOR r2;  dport_c DESC LIMIT 10 FOR r1
    update var i set
        r1[i]["server"] as srv_names[r1[i]["src"] | []]

    update var i set
        r2[i]["server"] as srv_names[r2[i]["src"] | []]

    write top_sender_dport.json from r1, 
        write_path/top_sender_dhost.json from r2


    # In this example, all the transmited ports and received ports are collected for per IP.
    # we will get the common ports as both transmited ports and recieved ports, and having the condition
    # of the number of shared ports should be bigger than 5. The code needs to use two steps:
    # 1. get all the transmited ports and received ports for per IP
    # 2. get the common port set and checking the condition.
    # the result should be written to a file

    read read_path/conn.json as flows, app_define/application_rule.json as application
    create {ip1:out_port} as r_src; {ip2:in_port} as r_dst 
    var i select
        flows[i]["id.orig_h"] as ip1;
        collect set(flows[i]["proto"].upper()+"_"+str(flows[i]["id.resp_p"])) group by ip1 as out_port;
        flows[i]["id.resp_h"] as ip2;
        collect set(flows[i]["proto"].upper()+"_"+str(flows[i]["id.resp_p"])) group by ip2 as in_port

    create {ip:comm_ports} as r 
    var ip, k select 
        r_dst[ip] as out_port; 
        r_src[ip | []] as in_port; 
        set(out_port) and  set(in_port) as comm_ports;
    where len(comm_ports) > 5
    write ip_to_comm_ports.json from r

