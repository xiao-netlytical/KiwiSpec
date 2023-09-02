## During the experiment with ChatGPT, we provided the following prompts to ChatGPT and generated Python code based on each prompt is listed below:

### Example 1:

Prompt:

    # With a json file which defines how an application server is classified based on the tcp 
    # and udp ports received and transmitted. 
    # And an API which can check the received ports and transmitted ports against the classification logic in the file.
    # Using a zeek connection log file in JSON as input, can you write code in Python3 
    # to  collect all the received ports and transmitted port, and map an ip to the classified application servers. 
    # The json file to classify an application server is in the format like this, 
    # [{
    #        "app_name": "app_name",
    #        "app_func": "app_function",
    #        "inbound_protocol": "((UDP_port0 and UDP_port1) or (UDP_port2 and UDP_port3))",
    #        "outbound_protocol": "((UDP_port0 and UDP_port1) or (UDP_port4 and UDP_port5))"
    #  }]
    # as an example.
    # Then write the mapping result to a output file.
    # hint to use to steps to get the final result: 
    # 1. aggregate all the transmitted file and received file for an IP
    # 2. apply the classification to the collected ports for per IP.

Generated Code:

    import json

    # Load the JSON file that classifies an application server based on TCP and UDP ports
    with open('app_servers.json', 'r') as f:
        app_servers = json.load(f)

    # Define a function to check whether a port matches a protocol expression
    def check_port(port, protocol_expr):
        return eval(protocol_expr.replace('port', str(port)))

    # Define a function to map an IP to the classified application servers
    def map_ip_to_app_servers(ip, conn_data):
        received_ports = set()
        transmitted_ports = set()
        
        # Aggregate all the transmitted and received ports for the IP
        for conn in conn_data:
            if conn['id.orig_h'] == ip:
                transmitted_ports.add(conn['id.resp_p'])
            if conn['id.resp_h'] == ip:
                received_ports.add(conn['id.orig_p'])
        
        app_servers_matched = []

        # Apply the classification to the collected ports for the IP
        for app_server in app_servers:
            inbound_matched = eval(app_server['inbound_protocol'].replace('UDP', 'received_ports').replace('TCP', 'received_ports'))
            outbound_matched = eval(app_server['outbound_protocol'].replace('UDP', 'transmitted_ports').replace('TCP', 'transmitted_ports'))
            if inbound_matched and outbound_matched:
                app_servers_matched.append(app_server)
        
        return app_servers_matched

    # Load the Zeek connection log file in JSON as input
    with open('conn.log.json', 'r') as f:
        conn_data = json.load(f)

    # Map each IP to the classified application servers
    ip_to_app_servers = {}
    for conn in conn_data:
        ip = conn['id.orig_h']
        if ip not in ip_to_app_servers:
            ip_to_app_servers[ip] = map_ip_to_app_servers(ip, conn_data)

    # Write the mapping result to an output file
    with open('ip_to_app_servers.json', 'w') as f:
        json.dump(ip_to_app_servers, f)

### Example 2:

Prompt:

    # with the ip to application server mapping generated by last generated code. 
    # Can you write Python3 code with the request for
    # Extrafiltration: based on the zeek log in json format, 
    # can you write Python3 code to get the sending bytes in total 
    # and the sending packets in total between two ip pair, 
    # the result should be sorted and limited to top 10
    # and using the result from the previous code generating ip to server mapping to 
    # update the result with 
    # server information for source ip and destination ip in the final result
    # the output should be in two files for top sending bytes and top sending packet count.

Generated Code:

    import json
    import requests

    # Load the ip to application server mapping file
    with open('ip_to_app_mapping.json', 'r') as f:
        ip_to_app_mapping = json.load(f)

    # Load the Zeek connection log file
    with open('conn.log.json', 'r') as f:
        conn_logs = json.load(f)

    # Aggregate the total bytes and packets sent between each IP pair
    byte_totals = {}
    packet_totals = {}
    for conn in conn_logs:
        src_ip = conn['id.orig_h']
        dest_ip = conn['id.resp_h']
        bytes_sent = conn['orig_bytes']
        packets_sent = conn['orig_pkts']
        key = (src_ip, dest_ip)
        if key not in byte_totals:
            byte_totals[key] = 0
        if key not in packet_totals:
            packet_totals[key] = 0
        byte_totals[key] += bytes_sent
        packet_totals[key] += packets_sent

    # Sort the results by total bytes and packets sent
    sorted_byte_totals = sorted(byte_totals.items(), key=lambda x: x[1], reverse=True)[:10]
    sorted_packet_totals = sorted(packet_totals.items(), key=lambda x: x[1], reverse=True)[:10]

    # Get the application server information for each IP
    def get_app_server_info(ip):
        # Use the ip_to_app_mapping to look up the app server info for the IP
        app_server_info = ip_to_app_mapping.get(ip, {})
        # Use an API to get more detailed info about the app server
        response = requests.get('https://example.com/api/app_server_info', params=app_server_info)
        if response.status_code == 200:
            app_server_info.update(response.json())
        return app_server_info

    # Add the app server info to the results
    byte_results = []
    for (src_ip, dest_ip), byte_total in sorted_byte_totals:
        byte_results.append({
            'src_ip': src_ip,
            'dest_ip': dest_ip,
            'byte_total': byte_total,
            'src_app_server': get_app_server_info(src_ip),
            'dest_app_server': get_app_server_info(dest_ip)
        })

    packet_results = []
    for (src_ip, dest_ip), packet_total in sorted_packet_totals:
        packet_results.append({
            'src_ip': src_ip,
            'dest_ip': dest_ip,
            'packet_total': packet_total,
            'src_app_server': get_app_server_info(src_ip),
            'dest_app_server': get_app_server_info(dest_ip)
        })

    # Write the results to output files
    with open('top_byte_totals.json', 'w') as f:
        json.dump(byte_results, f)

    with open('top_packet_totals.json', 'w') as f:
        json.dump(packet_results, f)

### Example 3:

Prompt:

    # In Python3, based on zeek log, can you get 
    # total onnection count and total durations between an IP pair for per protocol/port, 
    # and sort the result based the longest total duration and limit the result to 100 to an output file.
    # For per ip source, the application server info should be updated later based on the previous result from the code which
    # generates the ip to application mappings.
    # Keep in mind that order by and limit can be used with the same create.

Generated Code:

    import json

    # Read in the connection log file in JSON format
    with open('conn.log.json', 'r') as f:
        conn_log = json.load(f)

    # Read in the IP to application server mapping file
    with open('ip_to_app_mapping.json', 'r') as f:
        ip_mapping = json.load(f)

    # Create an empty dictionary to hold the result
    result = {}

    # Loop through each connection log entry
    for entry in conn_log:
        src = entry['id.orig_h']
        dst = entry['id.resp_h']
        proto = entry['proto']
        port = entry['id.resp_p']
        count = 1
        duration = entry['duration']

        # Check if the source and destination IPs are in the mapping file
        if src in ip_mapping and dst in ip_mapping:
            # Create a unique key for this IP pair and protocol/port combination
            key = f"{src}_{dst}_{proto}_{port}"
            # If the key exists in the result dictionary, update the count and duration
            if key in result:
                result[key]['total_count'] += count
                result[key]['total_duration'] += duration
            # Otherwise, create a new entry in the result dictionary
            else:
                result[key] = {
                    'src_ip': src,
                    'dst_ip': dst,
                    'proto': proto,
                    'port': port,
                    'total_count': count,
                    'total_duration': duration
                }

    # Sort the result based on the longest total duration
    sorted_result = sorted(result.values(), key=lambda x: x['total_duration'], reverse=True)[:100]

    # Update server info based on the IP to application server mapping file
    for entry in sorted_result:
        entry['src_server'] = ip_mapping[entry['src_ip']]
        entry['dst_server'] = ip_mapping[entry['dst_ip']]

    # Write the result to a JSON file
    with open('ip_pair_duration_count.json', 'w') as f:
        json.dump(sorted_result, f, indent=4)

### Example 4:

Prompt:

    # In Python3, base on the previous result generated by the KiwiSpec for top total duration, 
    # Find the common source IPs which are in both top total duration and top total bytes sender.

Generated Code:

    import json

    # Read in the output files from previous KiwiSpec code
    with open("top_duration.json", "r") as f:
        top_duration = json.load(f)

    with open("top_bytes.json", "r") as f:
        top_bytes = json.load(f)

    # Get a set of source IPs from top_duration
    ip_set = set([x["src_ip"] for x in top_duration])

    # Find common source IPs in both top_duration and top_bytes
    common_ips = [x for x in top_bytes if x["src_ip"] in ip_set]

    # Print the common source IPs
    print("Common source IPs:")
    for ip in common_ips:
        print(ip["src_ip"])