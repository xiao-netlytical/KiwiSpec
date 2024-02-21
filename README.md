# KiwiSpec
KiwiSpec (Knowledge Interpreter With Intelligence) is a declarative language developed for data processing by specifying relationships, constraints, and transformations as code on JSON-formatted datasets

The language is tailored for data access, manipulation, information extraction, and constraint validation on JSON-formatted datasets. KiwiSpec is designed with the goal of being close to natural language and easy to adopt, read, understand, and maintain. As a declarative language, KiwiSpec borrows the basic language structure from SQL while extending the capabilities to access and query JSON-formatted datasets. A query to a JSON field is defined as an expression with identifiers representing all the valid instances within a dataset.

Built upon expressions, programming data aggregation, transformation, and validation is streamlined to define the desired format and required relationships of expressions. In KiwiSpec, a tracing path can be specified with a root expression and extension expressions with constrains. The correlation of data fields from multiple data sources is simplified through layered expressions.

To capture comprehensive logic for integrating multiple independently held constraints, composite logic expressions are introduced. With composite expressions, each constraint is independently evaluated using the specified dataset, and the final result of a composite logic is the integration of the individual outcomes. Composite logic expressions consist of 'and/or' operations of the individual constraints, each of which is enclosed within parentheses and preceded by the leading word 'unit'.

KiwiSpec is an extension of the Python language, inheriting many Python operations such as string operations, list and set operations and logical expressions.

Key features of the KiwiSpec include:

    - Expressions with variables for accessing JSON fields
    - Data aggregation with group by and condition
    - Result sorting
    - Result limiting
    - Logic expressions as filters
    - Composite logic expressions for integrating independently held logic expressions
    - Path tracing for relationship chains
    - Output definition for result JSON structure


## 1. KiwiSpec and Interpreter

The key building blocks of the language are identifiers, expressions, and relationship operators. The following examples provide a quick preview of the language. The kiwiSpec interpreter can execute the following specs and write the result to the specified files.

The first example uses conn.log from Zeek to generate a map between an IP address to the provided services.

    READ conn_path/conn.json as flows; application_path/proto_desciption.json as proto_desciption
    CREATE {ip:apps} as result
    var i, k select 
        flows[i]["id.resp_h"] as ip;
        flows[i]["proto"].upper()+"_"+str(flows[i]["id.resp_p"]) as port;
        collect set(port+":"+proto_desciption[port]) group by ip as apps;
    where port not in ["TCP_443", "TCP_80"];
          flows[i]["conn_state"] in ["OTH", "SF", "S1", "S2", "S3", "RSTO", "RSTR"] and not flows[i]["proto"].startswith("icmp")
    write write_path/ip_to_servers.json from result
    
In the following example, connections are aggregated to an source application and destination application pair.

    READ write_path/ip_to_servers.json AS srv; conn_path/conn.json AS flows
    CREATE [{"s_srv":s_srv, "d_srv":d_srv, "o_pkts":o_pkts, "r_pkts":r_pkts, "protos": protos}] AS result
    VAR i SELECT
        srv[flows[i]["id.orig_h"]][_] AS s_srv;
        srv[flows[i]["id.resp_h"]][_] AS d_srv;
        SUM(flows[i]["orig_pkts"]) AS o_pkts;
        SUM(flows[i]["resp_pkts"]) AS r_pkts;
        COLLECT SET(flows[i]["proto"].upper()+"_"+str(flows[i]["id.resp_p"])) AS protos;
    where flows[i]["conn_state"] in ["OTH", "SF", "S1", "S2", "S3", "RSTO", "RSTR"]
    WRITE write_path/server_to_server_traffic.json FROM result

The following example uses conn.log from Zeek to generate a list of the top 5 DNS initiators in every 5 minutes interval.

    READ conn_path/conn.json AS flows
    CREATE {window_start: [{dns_src: dns_requests} LIMITED 10]}  AS result
    VAR i 
    SELECT
        flows[i]["id.orig_h"] AS dns_src;
        int(epoch_time(flows[i]["ts"])/300) AS window_start;
        COUNT DISTINCT(i) GROUP BY dns_src,window_start AS dns_requests;
        WHERE flows[i]["id.resp_p"] == 53;
        ORDER BY dns_requests DESC
    WRITE write_path/top_dns_sender.json FROM result

In this example, SMB calling paths are collected.

    READ read_path/conn.json AS flows; write_path/ip_to_servers.json AS srv
    create   [path_recording] as result
    var i, j select
        flows[i]["id.orig_h"] AS s_ip_1;
        flows[i]["id.resp_h"] AS d_ip_1;
        flows[j]["id.orig_h"] AS s_ip_2;
        flows[j]["id.resp_h"] AS d_ip_2;
        collect set ((s_ip_1, d_ip_1)) where d_ip_1 == s_ip_2 extend by (s_ip_2, d_ip_2) as path_recording;
    where flows[i]["id.resp_p"] in [445, 137, 138,139]; 
          flows[j]["id.resp_p"] in [445, 137, 138,139]
    WRITE write_path/path_recording.json FROM result

For more details on KiwiSpec, please refer to the Kiwilang directory. 

https://github.com/xiao-netlytical/kiwi/blob/main/kiwilang/kiwi.md
    
For additional examples, please see the files under the rules directories.


## 2. Rules in KiwiSpec:

KiwiSpec is employed in cybersecurity applications for Cyber Asset Attack Surface Management, threat hunting, and enforcing security policies.

Use cases encompass utilizing logs and configurations to explore IT/OT/Cloud environments, establishing baselines, identifying outliers, and validating configurations, deployments, and activities.
There are four sets of KiwiSpec rules organized under /rules subdirectories:

### 2.1 Application Discovery

Within the rules/application directory, a set of KiwiSpecs can be employed to discover servers from Zeek connection logs. Application servers are classified by using composite logic to define the required protocols for a server.

### 2.2 Learning the Environment

In the rules/asset directory, a set of KiwiSpecs is defined for discovering assets, applications, and services, as well as aggregating the assets and connections in different criteriaes. These KiwiSpecs explore the relationships and dependencies using various classification mechanisms. A subset of KiwiSpecs demonstrates how to create traffic permission policies based on the discovered activities and groups.

### 2.3 Baseline and Outlier

Under the rules/security directory, a set of KiwiSpecs demonstrates how to find top talkers, longest connections, per-interval statistics, and connection tracing paths. 

Another set of specifications is defined to validate best practices and security policies for cloud deployments.

## 3. To try KiwiSpec with the rules and a sample Zeek log
   
           git clone https://github.com/xiao-netlytical/kiwi.git 
           cd KiwiSpec
           mkdir sample_data/result 
           cd kiwilang
           python3 kiwi_main.py ../rules/application/application.kiwi
           python3 kiwi_main.py ../rules/asset/asset.kiwi
           python3 kiwi_main.py ../rules/asset/explore.kiwi
           python3 kiwi_main.py ../rules/asset/explore_service.kiwi
           python3 kiwi_main.py ../rules/security/security.kiwi
           python3 kiwi_main.py ../rules/security/cloud_policy.kiwi


The results are in files under sample_data/result.

The sample data is from https://github.com/brimdata/zed-sample-data with reduced size.


## If there are any inquiries, please contact me at xiao.netlytical@gmail.com
