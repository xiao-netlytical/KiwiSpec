# KiwiSpec
KiwiSpec (Knowledge Interpreter With Intelligence) is a project aimed at developing a declarative language for documenting data processing by specifying relationships and transformations as code based on semi-structured data in JSON format.

The language is tailored for data access, manipulation, information extraction, and constraint validation using JSON-formatted datasets. KiwiSpec is designed with the goal of being close to natural language and easy to adopt, read, understand, and maintain. As a declarative language, KiwiSpec borrows the basic language structure from SQL while extending the capabilities to access and query JSON data fields. A query to a JSON field is defined as an expression with identifiers representing all valid instances within the dataset.

Constructed on expressions, programming data aggregation, transformation, and validation are defining the desired format and required relationships of expressions. A trace path in KiwiSpec can be specified with a root expression and extensions with conditions. Correlating data fields from multiple sources is simplified through layered expressions.

To capture comprehensive logic for integrating multiple independently held constraints, composite logic expressions are introduced. With composite expression, each constraint is independently evaluated using the entire dataset, and the final result of a composite logic is the integration these individual outcomes. Composite logic expressions consist of 'and/or' operations of each 'units' leaded and parentheses enclosed constraint.

To capture comprehensive logic for integrating multiple independently held constraints, composite logic expressions are introduced. With composite expressions, each constraint is independently evaluated using the entire dataset, and the final result of a composite logic is the integration of these individual outcomes. Composite logic expressions consist of 'and/or' operations of the individual constraints, each of which is enclosed within parentheses and preceded by the leading word 'unit'.

KiwiSpec is an extension of the Python language, inheriting many Python operations such as string operations, lists and sets operations and logical expressions.

Key features of the KiwiSpec language include:

    Expressions with variables for accessing JSON fields
    Data aggregation with group by and condition
    Result sorting
    Result limiting
    Logic expressions for filtering specification
    Composite logic expressions for integrating independently held logic expressions
    Path tracing for relationship chains
    Output definition for result JSON structure


## 1. KiwiSpec and Interpreter

The key building blocks of the language are identifiers, expressions, and relationship operators. The following examples provide a quick preview of the language.

The first example uses conn.log from Zeek to generate a list of the top 5 DNS initiators in every 5 minutes interval.

    READ conn.json AS flows
    CREATE {window_start: [{dns_src: dns_requests} LIMITED 10]}  AS result
    VAR i 
    SELECT
        flows[i]["id.orig_h"] AS dns_src;
        int(epoch_time(flows[i]["ts"])/300) AS window_start;
        SUM(count_one(i)) GROUP BY dns_src,window_start AS dns_requests;
        WHERE flows[i]["id.resp_p"] == 53;
        ORDER BY dns_requests DESC
    WRITE top_dns_sender.json FROM result

In this example, path traces of the SMB connections are collected.

    READ read_path/conn.json AS flows; write_path/ip_to_servers.json AS srv
    create   [path_recording] as result
    var i, j select
        flows[i]["id.orig_h"] AS s_ip_1;
        flows[i]["id.resp_h"] AS d_ip_1;
        flows[j]["id.orig_h"] AS s_ip_2;
        flows[j]["id.resp_h"] AS d_ip_2;
        collect set ((s_ip_1, d_ip_1)) where d_ip_1 == s_ip_2 extend by (s_ip_2, d_ip_2) as path_recording;
    where flows[i]["id.resp_p"] == 445; flows[j]["id.resp_p"] == 445
    WRITE write_path/path_recording.json FROM result

For more details on KiwiSpec, please refer to the Kiwilang directory. 

https://github.com/xiao-netlytical/kiwi/blob/main/kiwilang/kiwi.md
    
For additional examples, please see the rules directories.


## 2. Rules in KiwiSpec:

KiwiSpec can be utilized in cybersecurity applications to specify asset discovery, threat hunting searches, and validation of security policies. The use cases include leveraging logs and configurations to explore IT/OT/Cloud environments, as well as to validate configurations, deployments, and activities for adherence to best practices and security policies.

The four sets of KiwiSpec applications are organized under subdirectories:

### 2.1 Application Discovery

Within the rules/application directory, a set of KiwiSpecs can be employed to discover servers in an environment from Zeek connection logs. Application servers are defined using composite logic expressions to specify a list of required protocols for each defined server.

### 2.2 Asset Discovery

In the rules/asset directory, a set of KiwiSpecs is defined for discovering assets, applications, and services, as well as aggregating the assets and connections. These KiwiSpecs explore relationships and dependencies using various classification mechanisms. A subset of KiwiSpecs demonstrates how to create traffic permission policies based on the discovered activities and groups.

### 2.3 Security Rules

Under the rules/security directory, a set of KiwiSpecs demonstrates how to find top talkers, longest connections, per-interval statistics, and trace paths. Another set of specifications is defined to validate best practices and security policies for cloud deployments.

## 3. To try KiwiSpec with the rules and a sample Zeek log
   
           git clone https://github.com/xiao-netlytical/kiwi.git 
           cd kiwi
           mkdir sample_data/result 
           cd kiwilang
           python3 kiwi_main.py ../rules/application/application.kiwi
           python3 kiwi_main.py ../rules/asset/asset.kiwi
           python3 kiwi_main.py ../rules/asset/explore.kiwi
           python3 kiwi_main.py ../rules/asset/explore_service.kiwi
           python3 kiwi_main.py ../rules/security/security.kiwi
           python3 kiwi_main.py ../rules/security/threat_hunt.kiwi
           python3 kiwi_main.py ../rules/security/cloud_policy.kiwi


The results are in files under sample_data/result.

The sample data is from https://github.com/brimdata/zed-sample-data with reduced size.


## If there are any inquiries, please contact me at xiao.netlytical@gmail.com
