
### Summary:
We conducted an experiment using ChatGPT to generate data processing code for security applications in a newly developed declarative language called KiwiSpec.

KiwiSpec is an open source project that seeks to create a language and platform for processing semi-structured data using a declarative approach, as opposed to the relational databases used for flat tables. 

Our aim was to explore the potential of using ChatGPT to generate code in a new language. We also studied the prompts provided to ChatGPT for this task, as well as the post-generation work required to modify the code.

The experiment showed the advantages of using KiwiSpec at the post-generation stage due to its declarative nature, which makes it easier to understand, proofread, and modify the generated code. 

If you're interested in learning more about this experiment, in this folder, you can find the prompts we provided for ChatGPT to learn KiwiSpec, as well as more code examples and comparisons in KiwiSpec and Python3.



### Experiment:

Here are the steps, some conversations, and generated code produced by ChatGPT:

To teach ChatGPT about KiwiSpec, we provided it with a set of examples that included requirements and implemented code. You can find this example set in the file examples_for_chatgpt.md.

We then asked ChatGPT to generate the code separately in KiwiSpec and Python.

#### Experiment 1:

We gave the following prompt to ChatGPT to classify application servers from zeek connection log.

    # Here are a requirement for the code in KiwiSpec:  
    # With a json file which defines how an application server is classified based on the tcp 
    # and udp ports received and transmitted. 
    # And an API which can check the received ports and transmitted ports against the classification logic in the file.
    # Using a zeek connection log file in JSON as input, can you write code in KiwiSpec 
    # to  collect all the received ports and transmitted port, and map an ip to the classified application servers. 
    # The json file to classify an application server is in the format like this, 
     [{
            "app_name": "app_name",
            "app_func": "app_function",
            "inbound_protocol": "((UDP_port0 and UDP_port1) or (UDP_port2 and UDP_port3))",
            "outbound_protocol": "((UDP_port0 and UDP_port1) or (UDP_port4 and UDP_port5))"
        }]
    # as an example.
    # Then write the mapping result to an output file.
    # hint to use to steps to get the final result: 
    # 1. aggregate all the transmitted file and received file for an IP
    # 2. apply the classification to the collected ports for per IP.

ChatGPT replied as following: 

    Sure, here's an example implementation in KiwiSpec:

        # Define input parameters
        parameter input_file: string = "path/to/zeek/connection/log.json"
        parameter classification_file: string = "path/to/app/classification.json"
        parameter output_file: string = "path/to/output/file.json"

        # Read input files
        read input_file as flows
        read classification_file as classifications

        # Step 1: Aggregate all the transmitted and received ports for each IP
        create {ip: out_ports} as outbound_ports
        create {ip: in_ports} as inbound_ports
        var i select
            flows[i]["id.orig_h"] as ip;
            collect set(flows[i]["proto"].upper() + "_" + str(flows[i]["id.resp_p"])) group by ip as out_ports;
            flows[i]["id.resp_h"] as ip;
            collect set(flows[i]["proto"].upper() + "_" + str(flows[i]["id.orig_p"])) group by ip as in_ports

        # Step 2: Apply the classification to the collected ports for each IP
        create {ip: app_servers} as app_servers
        var ip, k, l select
            classifications[k]["app_name"] as app_name;
            classifications[k]["app_func"] as app_func;
            classifications[k]["inbound_protocol"] as inbound_protocol;
            classifications[k]["outbound_protocol"] as outbound_protocol;
            inbound_protocol is satisfied by inbound_ports[ip] and outbound_protocol is satisfied by outbound_ports[ip] as match;
            if match then {app_name: app_func} else {} as app_servers;
        where match
        write output_file from app_servers

    This code reads in a Zeek connection log file in JSON format and a JSON file that defines how an application server is classified based on its transmitted and received ports. It then aggregates all the transmitted and received ports for each IP and applies the classification logic to the collected ports. Finally, it writes the mapping results to an output file.

The identifier 'l' in the generated code is not used later on, and the line "if match then {app_name: app_func} else {} as app_servers;" should be rewritten as "{app_name: app_func} where match | {} as app_servers;"

#### Experiment 2:

To retrieve information about Extrafiltration and attach the classified server information to the top senders, we provided ChatGPT with the following prompt:"

    # with the ip to application server mapping generated by last generated code. 
    # Can you write KiwiSpec code with the request for
    # Extrafiltration: based on the zeek log in json format, 
    # can you write KiwiSpec code to get the sending bytes in total 
    # and the sending packets in total between two ip pair, 
    # the result should be sorted and limited to top 10
    # and using the result from the previous code generating ip to server mapping to 
    # update the result with 
    # server information for source ip and destination ip in the final result
    # the output should be in two files for top sending bytes and top sending packet count.

ChatGPT replied as following: 

    require "json";

    # Read IP to application server mapping
    read ip_to_server_mapping.json as ip_server_map;

    # Read Zeek connection log file in JSON format
    read conn.json as zeek_log;

    # Define result data structures
    create {src_ip: dst_ip, bytes_sent: 0} as bytes_sent_per_pair;
    create {src_ip: dst_ip, packets_sent: 0} as packets_sent_per_pair;

    # Aggregate sending bytes and packets for each IP pair
    var i select
        zeek_log[i]["id.orig_h"] as src_ip;
        zeek_log[i]["id.resp_h"] as dst_ip;
        sum(zeek_log[i]["orig_bytes"]) as bytes_sent;
        sum(zeek_log[i]["orig_pkts"]) as packets_sent;

    # Only keep IP pairs with non-zero sending bytes and packets
    where bytes_sent > 0 or packets_sent > 0;

    # Update result data structures with server information for source IP and destination IP
    update var i set
        bytes_sent_per_pair[i]["src_server"] as ip_server_map[src_ip | ""];
        bytes_sent_per_pair[i]["dst_server"] as ip_server_map[dst_ip | ""];
        packets_sent_per_pair[i]["src_server"] as ip_server_map[src_ip | ""];
        packets_sent_per_pair[i]["dst_server"] as ip_server_map[dst_ip | ""];

    # Sort and limit results to top 10 sending bytes and packets
    order by bytes_sent desc limit 10 for bytes_sent_per_pair;
    order by packets_sent desc limit 10 for packets_sent_per_pair;

    # Write results to output files
    write top_sending_bytes.json from bytes_sent_per_pair;
    write top_sending_packets.json from packets_sent_per_pair;

Moving the 'update' statement after 'order by' and 'limit' in the generated code can improve its performance.


#### Experiment 3:

We provided the following prompt to ChatGPT to identify the longest connection or concatenation of connections.

    # In kiwiSpec, based on zeek log, can you get the longest connection or 
    # longest concatenated connections between an IP pair for per protocol, 
    # and sort the result based the longest and limit to 100 as the result to a file.

ChatGPT:

    read zeek_conn_json as conn_logs
    create {src_ip, dest_ip, protocol, duration} as r
    var i select 
        conn_logs[i]["id.orig_h"] as src_ip; 
        conn_logs[i]["id.resp_h"] as dest_ip; 
        conn_logs[i]["proto"] as protocol;
        conn_logs[i]["duration"] as duration;

    create {src_ip, dest_ip, protocol, total_duration} as r2
    var src_ip, dest_ip, protocol, total_duration select 
        sum(duration) group by src_ip, dest_ip, protocol as total_duration;
        
    create {src_ip, dest_ip, protocol, total_duration} as r3
    var src_ip, dest_ip, dest_ip, protocol, total_duration
        select src_ip, dest_ip, protocol, total_duration 
        group by src_ip, dest_ip, protocol
        sort by total_duration descending
        limit 100;
        
    create {src_ip:app_name, dest_ip:app_name} as app_info
    read app_json as app_rules;
    var i select
        app_rules[i]["inbound_protocol"] as inbound_protocol;
        app_rules[i]["outbound_protocol"] as outbound_protocol;
        app_rules[i]["app_name"] as app_name;
        create {app_name} as r select 
            src_ip where eval(inbound_protocol) or dest_ip where eval(outbound_protocol) as ip;
        
    update r3 with app_info on src_ip, dest_ip as app_info_r3;
        
    write longest_conn_top100_duration.json from r3;

This answer contained several errors and was inconsistent with the previous responses. It also made us realize that we actually wanted to obtain the top duration of the aggregated connections. Therefore, we modified the prompt as follows and provided it to ChatGPT:

    can you try to write code in KiwiSpec for: 
    # In kiwiSpec, based on zeek log, can you get 
    # total onnection count and total durations between an IP pair for per protocol/port, 
    # and sort the result based the longest total duration and limit the result to 100.
    # the out ip, count and duration should be in list of dictionary written to a file.
    # For per ip source, the application server info should be updated later based on the previous result from the code which
    # generates the ip to application mappings.
    # Keep in mind that order by and limit can be used with the same create.

At this point, it seems that ChatGPT had forgotten the knowledge it gained on KiwiSpec and generated code that did not align well with KiwiSpec. Therefore, we decided to reinforce ChatGPT's understanding of KiwiSpec by providing it with the following prompt.

    not close, here is an example: 
    READ  server.json AS srv, conn.json AS flows
    CREATE [{"server": s_srv, "outbound_count": ip_c, "total_pkts": pkts}] AS r
    VAR i SELECT 
        srv[flows[i]["id.orig_h"]][_] AS s_srv;  
        COUNT DISTINCT(flows[i]["id.resp_h"]) AS ip_c;
        SUM(flows[i]["orig_pkts"]) AS pkts;
    WHERE is_internet_ip(flows[i]["id.resp_h"])
    WRITE server_access_internet_cnt.json FROM r

Then ChatGPT provided an answer that was very close, but it missed the server information:

    Apologies for the confusion earlier. Here's the modified code based on the examples you provided:

        READ conn.log AS conn, zeek.json AS zeek

        CREATE [{"src_ip": src, "dst_ip": dst, "protocol": proto, "port": port, "total_duration": duration, "connection_count": count}] AS result

        VAR i SELECT
        conn[i]["id.orig_h"] AS src;
        conn[i]["id.resp_h"] AS dst;
        zeek[conn[i]["uid"]]["conn"]["proto"] AS proto;
        zeek[conn[i]["uid"]]["conn"]["resp_p"] AS port;
        zeek[conn[i]["uid"]]["conn"]["duration"] AS duration;
        COUNT(*) AS count;
        WHERE is_internet_ip(conn[i]["id.resp_h"])

        ORDER BY duration DESC LIMIT 100

        WRITE connection_stats.json FROM result


Experiment 3 did not proceed smoothly, as it required several iterations of back-and-forth to make the necessary changes. However, after some effort, we were able to produce two versions that close to our desired outcome.

version 1:

    read read_path/conn.json as flows
    read read_path/ip_to_app_server.json as ip_to_app_server

    create [{"src_ip": src_ip, "dst_ip": dst_ip, "proto": proto, "port": port, "conn_count": conn_count, "total_duration": total_duration, "server_info": server}] as r
    var src_ip, dst_ip, proto, port, k select
        flows[k]["id.orig_h"] as src_ip;
        flows[k]["id.resp_h"] as dst_ip;
        flows[k]["proto"] as proto;
        str(flows[k]["id.resp_p"]) as port;
        sum(1) group by src_ip, dst_ip, proto, port as conn_count;
        sum(flows[k]["duration"]) group by src_ip, dst_ip, proto, port as total_duration;
        ip_to_app_server[src_ip] as server;
    where total_duration > 0
    order by total_duration desc
    limit 100
    write output_path/top_100_connections.json from r

version 2:

    READ conn.json AS conn;
    READ ip_to_app_mapping.json AS ip_mapping;
    READ server_info.json AS server_info;

    CREATE 
        [{"src_ip": src, "dst_ip": dst, "proto": proto, "port": port, "total_count": count, "total_duration": duration, "src_server": src_server, "dst_server": dst_server}] AS result
    VAR i SELECT 
        conn[i]["id.orig_h"] AS src; 
        conn[i]["id.resp_h"] AS dst; 
        conn[i]["proto"] AS proto; 
        conn[i]["id.resp_p"] AS port; 
        COUNT(conn[i]) AS count; 
        SUM(conn[i]["duration"]) AS duration; 
        ip_mapping[src]["server"] AS src_server; 
        ip_mapping[dst]["server"] AS dst_server
    WHERE 
        ip_mapping[src] IS NOT NULL AND ip_mapping[dst] IS NOT NULL
    WRITE ip_pair_duration_count.json FROM result ORDER BY duration DESC LIMIT 100;

#### Experiment 4:

We provided ChatGPT with the following prompt to identify the common set of source IPs that appear in both the top duration list and the top byte sender list.

    #In KiwiSpec, base on the previous result generated by the KiwiSpec for top total duration, Find the common source IPs which are in both top total duration and top total bytes sender.

ChatGPT's answer:

    READ top_duration.json AS td, top_bytes.json AS tb
    CREATE [{"src_ip": td[i]["src_ip"], "total_duration": td[i]["total_duration"], "total_bytes": tb[j]["total_bytes"]}]
        AS result
    VAR i, j
    SELECT DISTINCT(td[i]["src_ip"]) AS src_ip
    WHERE td[i]["src_ip"] == tb[j]["src_ip"]
    ORDER BY td[i]["total_duration"] DESC, tb[j]["total_bytes"] DESC
    LIMIT 100
    WRITE common_ips.json FROM result

Although the sorting and limiting are not in the requirement.

