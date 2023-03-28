
# KiwiLang: A Declarative Approach to Semi-Structured Data Processing

xiao-netlytical@google.com

## Description:

Kiwilang is a project that provides a method for specifying data processing logic in a declarative manner. The solution aims to offer a language and a generic platform for specifying data processing logic in a semi-structured format, managing and executing the specifications in Kiwilang. The interested data processing includes searching and retrieving data with filters, data aggregation, data correlation, data transformation, recursive computation, and trending reports.

To build a specification for data processing of semi-structured data, Kiwilang uses expressions with identifiers representing the possible instantiations in a semi-structured data path to access a data value. Additionally, Kiwilang provides operators to create more complex computational expressions with conditional logic and sorting. Together, the declarative language and the specification include constructs to build expressions, specify data input sources, create output templates, and build pipelines.

In addition to the language aspect, the Kiwilang platform also aims to provide a generic platform to manage, translate, and execute specifications, as well as manage and display outputs.

Furthermore, Kiwilang can also be used as an extension to any imperative language. By embedding the declarative specification for data processing into Python code, the data processing logic can be translated to Python code and executed with the rest of the code.

## Background:

The Kiwilang project was conceived to provide a specification language that can document the data processing logic for applications in areas such as Cyber Asset Attack Surface Management (CAASM), Zero Trust analytics, and threat hunting.

In these applications, the processing of log data and metadata is a critical component in the generation of insights. Products developed in these areas provide users with functionalities to identify critical assets, understand the relationships between workloads and application servers, detect violations, and surface risk factors from traffic logs, configurations, installations, and upgrade logs.

Creating such applications requires domain expertise to produce valuable insights from the collected data, and the system needs to be kept updated with new learnings. The Kiwilang project aims to address these needs by providing a language that enables domain experts to document their knowledge and rules easyly, as well as a generic platform capable of managing and interpreting those knowledge and applying them to the collected data.

The applications in the interested areas have common requirements in terms of data processing. The desired commonality of data processing includes retrieving, searching, filtering, transforming, aggregating, correlating, recursive computing, and trending.

In detail, the data processings can be defined as:

• Searching and retrieving: Select matching data as output from multiple inputs.

• Searching with filtering: Select matching data that meets condition computations as output from multiple inputs.

• Transformation: From the selected data, generate output after recomputing.

• Aggregation: Collect a set of data, collect a distinct set, calculate sum, count, count distinct, min, max, mean, all, any, and states grouped by some values.

• Correlation: Correlate data entries within the same input or multiple inputs.

• Recursive computation: Compute relationships recursively which match the specified condition along a path.

• Trending: Interval-based aggregation or state calculation with changing or trending reports.

• Projection: Final presentation of the processed data.

## Specification and Language:

The Kiwilang project aims to provide domain experts with a declarative language and platform to describe their data processing logic in an easily adoptable, readable, writable, and maintainable manner. The platform is designed to facilitate fast building and turnaround time with new security learnings.

The declarative specification and language should allow domain experts to:

. Specify input data in semi-structured format from any storage of memory, file, cloud storage, and/or database.

. Focus on the specification of the data transformation from input to output.

. Focus on describing data processing rules and logic.

. Use a rich language to specify the needed data processing.

. Use a language that is easy to adopt and understand.

. Write specifications that are easy to read and maintain.


To enable domain experts to describe their data processing logic in a declarative manner, the language and specification of Kiwilang should provide clear ways to specify the source of input data, data filtering and computation logic, output format, and target output storage. Kiwilang achieves this through five main constructs used to build a declarative specification:

• READ: For reading input data from various sources such as memory, file, cloud storage, and/or database.

• SELECT with condition, sorting, and limiting: For specifying data processing logic. This clause enables users to select and filter data from multiple inputs, transform the data, aggregate and correlate the data, perform recursive computation, and generate trending reports.

• WITH: For pipelining output from a section to input of another section with user-defined data structures.

• CREATE/UPDATE: For building output data structures. This clause enables users to create or update data structures that are needed for the output.

• WRITE: For writing output to targets such as memory, file, cloud storage, and/or database.

## Expression and Language:

The fundamental building block of kiwilang is expressions and identifiers. A basic expression is a path expression with identifiers in a semi-structured data path to access a data value. Compositional expressions is introduced to build more complext logic. Compositional expressions can be composed from basic or compositional expressions using operators including COLLECT, COLLECT DISTINCT, GROUP BY, ORDER BY, WHERE, CASE/END, LIMIT, SUM, COUNT, COUNT DISTINCT, MIN, MAX, MEAN, ALL, ANY, LAMBDA and REPEAT. With these operators, expressions can describe the logic of searching with filtering, math and logic computation, aggregation, correlation, transformation and recursive computations.
By introducing identifiers as placeholders for all the possible instatiations, the declarative language allows users to focus on describing data processing and transformation from input to output, without worrying about walking and manipulating data structures step-by-step.

Expressions can comprise paths accessing data values from multiple data structures. The same identifiers can be used along the path to access values in different levels of the data structures.  An expression accessing a value from one data structure can be used in a path to access another data structure. In these ways, multiple data sources are correlated. The WHERE operator can also be used to correlate multiple data entries or data sources by specifying the relationships between expressions. Different identifiers accessing the same data entry represent different instantiations which can be used to create a correlation between the entries. Relationship definition between entries can be used to build a recursive chain. A lambda operator is used to describe those relationships. An expression built by REPEAT operator with lambda function generates a list of objects along the recursive chain.

An expression calculated as a true or false value with identifier instantiated can serve as a condition expression. An expression can be followed by a condition keyword and a condition expression to form a compositional expression. An expression with an aggregation operator COLLECT, COLLECT DISTINCT, SUM, COUNT, COUNT DISTINCT, ANY, ALL, MIN, MAX, or MEAN forms an aggregation expression. An aggregation expression can be followed with GROUP BY and ORDER BY keyword with an expression or identifier names. Expression build from COLLECT operator or REPEAT operator will generate a set with or without unique values. An aggregation expression generating a set value as a result can be followed by an ORDER BY keyword to define the order of a set. Multiple expressions with condition operators can be grouped together by CASE operator to form a multi-choice expression.

Kiwilang borrows several keywords from SQL, including SELECT, WHERE, AS, GROUP BY, and ORDER BY, because they are widely adopted and self-explanatory. In SQL, the SELECT clause implies table row instantiations as the imperative procedure. In Kiwilang, however, users have more freedom with expressions and identifiers, and the underlying procedures allows any instantiation of identifiers with the calculated expressions. In this way, Kiwilang offers a more flexibility to specify data manipulation, while still drawing upon familiar and widely used keywords.

In this example, Kiwilang allows users to specify variables i and j and then select data[i].interest and data[j].interest, where the condition data[i].interest == data[j].interest is met.

    VAR i, j SELECT data[i].interes; data[j].interes; where data[i].interes == data[j].interes

A kiwilang specification is made from the constructs of READ, SELECT, WITH, CREATE, and WRITE.
Expressions are specified with SELECT clause are assigned a name with AS or FROM keywords. Expression names can be referred by other expressions or output templates. 
Within the SELECT construct, the WHERE, GROUP BY, or ORDER BY clauses can be used as a separate clause to apply the clause to all the expressions globally.
A kiwilang specification can include a READ clause to specify data sources from a file, storage, a data structure name, or a database.
A kewilang specification can include a WITH cluase to pipeline an output of a specification to an input of another specification.
A kewilang specification can include a  WRITE clause to specify an output to a file, a storage, a data structure name, or in a database.


## Output Template, Semantics, and Result Generation:

Kiwilang provides a CREATE construct that allows users to build outputs from expressions. The CREATE construct and clause use templates to define the outputs, which specify how to project the calculated expressions and identifiers as desired by the user. The templates are in semi-structured format and built from expression and identifier names assigned by the SELECT clause. The AS keyword binds an expression to an expression name, while the FROM keyword declares an identifier name for output. All the expressions and identifiers referred to by a template are grouped together to form an expression tuple.

The algorithm to generate final outputs based on specifications in Kiwilang involves two calculation phases.

The first phase is Identifier Instantiation, Expression Calculation, and Tuple Materialization. 

By instantiating identifiers with valid values, expressions can be materialized. A valid tuple value is formed by a valid set of identifier instantiations and expression calculations that also satisfy the condition clauses. The resulting tuple set is collected as a non-redundant set of all the valid tuple values.

The second phase of the computation is output projection. The final outputs are defined by one or more templates specified in a CREATE clause. Each template specifies how the output should be projected from the resulting tuple set. Since the resulting tuple includes the collection of referred expressions and identifiers, the template can be populated by each tuple value. The whole output set is generated by appending each population of the template.

An interpreter is implemented to convert a specification to executable code. The translated Python code, for example, will execute the above semantics and algorithm. The Kiwilang interpreter also combines, pipelines, and optimizes the loops with the instantiation and calculation to achieve the best performance.

As a complete solution, a platform is also under development to manage specifications, data sources, and outputs. The platform will provide an interface for plugging in the specifications and scheduling executions of the specifications.


## Examples:

The following is a list of examples of data processing specifications in the applications of CAASM, risk analysis, and threat hunting. These specifications are written in kiwilang and use JSON format for input and output data structures.

The input files are JSON files that are converted from the conn.log generated by Zeek. 
Each log entry in the conn.log contains the following fields:

id.resp_h  - destination IP of a connection
id.orig_h   - source IP of a connection
orig_pkts  - packet count from source to destination
resp_pkts - packet count from destination to source
proto        -  protocol of a connection
id.resp_p -  destination port 
ts             - connection starting time 

Example 1:

In this example, the following specification describes the data processing for collecting all the IP addresses that are either the source or destination IP in the conn.json file.

                READ conn.json AS flows
                CREATE ips AS r
                VAR i
                SELECT
                COLLECT DISTINCT(flows[i][“id.resp_h”]  |  flows[i][“id.orig_h"]) AS ips
                WRITE workloads.json FROM r

In the specification above:
•	READ: reads input data from the conn.json file.
•	“i”: is an identifier used to access a connection entry. flow[i] represents any valid connection entry.
•	flows[i][“id.resp_h"]: the destination IP of a connection entry.
•	flows[i][“id.orig_h"]: the source IP of a connection entry.
•	|: produces a valid result from either expressions, a source IP or a destination IP in this example.
•	COLLECT DISTINCT: collects distinct source IPs and destination IPs.
•	SELECT .. AS ..: assigns a name to an expression.
•	CREATE: defines an output; in this example, it is the result of the collection.
•	WRITE: writes the output to the workloads.json file.

Example 2:

In this example, the following specification describes the data processing of aggregating connections between a source and a destination. For each source and destination pair, packet counts of sending and receiving are added up. Protocol:ports are aggregated as a list, and a total flow number is counted.

            READ conn.json AS flows
            CREAT  
                [{"src":s_ip, "dst":d_ip, "o_pkts_ct”:o_pkts, "r_pkts_ct”:r_pkts, "service”:proto, "flows": count}] AS result
            VAR  i 
            SELECT
                flows[i]["id.orig_h"] AS s_ip;
                flows[i]["id.resp_h"] AS d_ip;
                SUM(flows[i]["orig_pkts” | 0]) AS o_pkts;
                SUM(flows[i]["resp_pkts” |  0]) AS r_pkts; 
                SUM(count_one(i))  AS count;
                COLLECT DISTINCT(flows[i]["proto”]+”:”+str(flows[i]["id.resp_p"])) AS proto
            WRITE  traffic_agg.json FROM result

In the specification above:
•	By default, aggregation will be grouped by all the non aggregating expressions in the result.
•	In this example, aggregations are grouped by (s_ip, d_ip) by default.
•	VAR i: used as an identifier to access a connection entry flow[I].
•	SUM: sum of flows[i]["orig_pkts”] if flows[i] has field "orig_pkts”.
•	flows[i]["orig_pkts” |  0]: If a flow entry does not have field “orig_pkts” or“"resp_pkts” field, 0 will be  used instead.
•	flows[i]["proto”]+”:”+str(flows[i]["id.resp_p”]): string concatenation.
•	SELECT .. AS .. : define a set of expressions and assign a name to an expression.
•	CREATE: define the output as a list of dictionaries, each dictionary is populated by a valid expressions tuple, the result dictionary is added to the list.

Example 3:

In this example,  the following specification describes the data processing of getting the top 10 IPs which initiate the most distinct outbound requests. 
Using a log file generated by Zeek as input,  the number of distinct outbound request of per protocol:port from a source IP is counted. In addition, the total packet and byte count for each source IP are also collected.
The final output is a sorted list of the top 10 dictionaries, with each dictionary containing information about the source IP, packet count, byte count, and service count. The output is also written to the "top_out_rel.json" file.

                READ conn.json AS flows
                CREATE
                    [{"ip": source_ip, "pkts": pkts, "bytes":bytes, "out_request": out_request} LIMIT 10] AS result
                VAR i 
                SELECT
                    flows[i]["id.orig_h"] AS source_ip;
                    COUNT DISTINCT(flows[i]["proto”]+”:”+str(flows[i]["id.resp_p"])) AS out_request;
                    SUM(flows[i]["orig_pkts”, 0] + flows[i]["resp_pkts”] | 0]) AS pkts;
                    SUM(flows[i][“orig_bytes", 0] + flows[i][“resp_bytes" | 0]) AS bytes;
                ORDER BY out_request DESCENT
                WRITE top_out_rel.json FROM result

In the specification above:
•	COUNT DISTINCT: counts the total number of distinct proto:port aggregated by a source IP.
•	ORDER BY:  the result tuples are ordered by the out_request count.
•	LIMIT:  the output list is limited to the first 10 dictionaries.

Example 4:

In this example, the following specifications describe the data processing  to identify a destination IP as an application server. The classification of an application server is based on its inbound and outbound protocol:port data, which is obtained from connection logs generated by Zeek. The server_definition.json file defines the required inbound and outbound protocol:ports to classify a server.

In section 4.1, the output is defined as a relationship between an IP address and the applications it supports. In section 4.2, the output is defined as a relationship between an application and all the IPs associated with it.

4.1
                READ conn.json AS flows, server_rule_data.json AS application
                CREATE [{“ip”:ip, “server”:apps}] AS r 
                VAR i 
                SELECT
                    flows[i]["id.orig_h"] AS ip1;
                    COLLECT DISTINCT(flows[i]["proto"].upper()+"_"+str(flows[i]["id.resp_p"])) GROUP BY ip1 AS out_port
                    flows[i]["id.resp_h"] AS ip2;
                    COLLECT DISTINCT(flows[i]["proto"].upper()+"_"+str(flows[i]["id.resp_p"])) GROUP BY ip2 AS in_port

                WITH {ip1:out_port} AS r_src, {ip2:in_port}  AS r_dst

                VAR ip, k 
                SELECT
                    r_dst[ip] AS out_port; 
                    r_src[ip | []] AS in_port; 
                    COLLECT DISTINCT(application[k][“Server Name”]) GROUP BY ip AS apps;
                WHERE 
                    eval_logic_expr(application[k]["Outbound Detection Logic"], out_port);
                    eval_logic_expr(application[k]["Inbound Detection Logic"], in_port)
                WRITE server.json FROM r

4.2
                READ conn.json AS flows, server_rule_data.json AS application
                CREATE [{“ip”:ips, “server”:app}] AS r 
                VAR i 
                SELECT
                    flows[i]["id.orig_h"] AS ip1;
                    COLLECT DISTINCT(flows[i]["proto"].upper()+"_"+str(flows[i]["id.resp_p"])) GROUP BY ip1 AS out_port
                    flows[i]["id.resp_h"] AS ip2;
                    COLLECT DISTINCT(flows[i]["proto"].upper()+"_"+str(flows[i]["id.resp_p"])) GROUP BY ip2 AS in_port

                WITH {ip1:out_port} AS r_src, {ip2:in_port}  AS r_dst

                VAR ip, k 
                SELECT
                    r_dst[ip] AS out_port; 
                    r_src[ip | [ ]] AS in_port; 
                    application[k]["Server Name"]) AS app;
                    COLLECT DISTINCT(ip) group by app AS ips;
                WHERE 
                    eval_logic_expr(application[k]["Outbound Detection Logic"], out_port);
                    eval_logic_expr(application[k]["Inbound Detection Logic"], in_port)
                WRITE server.json FROM r

In the specifications above:
•	By using WITH,  the output of one processing step can be passed on to another processing step.

Example 5:

In this example, the following specification describes the data processing for identifying the top 5 DNS initiators in 5-minute intervals. During each interval, the number of DNS requests is tallied for each source IP address. The resulting tuples (window, requesting IP address, and number of requests) are sorted by the number of requests. The final output is a list of the top 5 source IPs and their respective number of requests for each 5-minute interval, ranked by the number of requests.

                READ conn.json AS flows
                CREATE {window_start: [{dns_src: dns_requests} LIMITED 5]}  AS result
                VAR i 
                SELECT
                    flows[i]["id.orig_h"] AS dns_src;
                    int(epoch_time(flows[i]["ts"])/300) AS window_start;
                    SUM(count_one(i)) AS dns_requests;
                    WHERE flows[i]["id.resp_p"] == 53;
                    ORDER BY dns_requests DESCENT
                WRITE top_dns_sender.json FROM result

In the specification above:
•	DNS:  requests are grouped by non-aggregating values: dns_src and window_start.
•	WHERE:  clause filters the flow[i] for DNS requests.
•	ORDER BY: The result tuples are ordered by the number of DNS requests using the ORDER BY clause.
•	LIMIT: For each window, the top 5 source IPs with the highest DNS request count are added to the list using a LIMIT clause.

Example 6:

In this example, the following specifications describe collecting connections as a path linked by RDP connections, where each connection's destination is the next connection's source. Data collection starts with an internet IP address.

In example 5.1, the path length is limited to 5,  the logged source IP along the path is limited to application servers.
In example 5.2,  only the last IP address along the path is logged. 

6.1
                READ conn.json AS flows, server.json AS srv
                CREATE {src_ip: path_recording} AS result
                VAR i 
                SELECT
                flows[i]["id.orig_h"] AS src_ip;
                REPEAT(LAMBDA x:  VAR j 
                        COLLECT DISTINCT(flows[j][“id.resp_h”]) AS dst_ips                           
                        WHERE flows[j][“id.resp_p”] == 3389 AND flows[j][“id.orig_h"] == x
                        RETURN dst_ip
                        LOG  x WHERE x in srv.keys() and x != src_ip, src_ip, 5) AS path_recording
                WHERE internet_ip(src_ip)
                WRITE path_recording.json FROM result

6.2
                READ conn.json AS flows
                CREATE {src_ip: path_recording}  AS result
                VAR i 
                SELECT
                flows[i]["id.orig_h"] AS src_ip;
                REPEAT(LAMBDA x: VAR j 
                        COLLECT DISTINCT(flows[j][“id.resp_h”]) AS dst_ips                
                        WHERE flows[j][“id.resp_p”] == 3389 AND flows[j][“id.orig_h"] == x
                        RETURN  dst_ips
                        LOG  x  WHERE dst_ips == [] and x != src_ip, src_ip) AS path_recording
                WHERE internet_ip(src_ip) 
                WRITE path_recording.json FROM result

In the specifications above:
•	REPEAT: takes three parameters: the lambda definition, the first inputs of the lambda call, and the repeat limit.
•	The output of the LAMBDA call is either objects or a list of objects with the same type. This output can be used as input for the next LAMBDA call, or as a list of inputs for a loop of LAMBDA calls.
•	LAMBDA:  is defined with input and output elements, where the output elements become the next inputs, and the logged elements become the final output of the REPEAT. The RETURN keyword specifies the output elements, while the LOG keyword specifies the logged elements.
•	RETURN:  returns objects or a list of objects that become inputs of the next LAMBDA call.
•	LOG:  specifies the objects that are appended to the final result of the REPEAT computation.

## Conclution:

In conclusion, the Kiwilang project aims to provide a declarative language and platform for specifying data processing logic for semi-structured data. The key technical aspects of Kiwilang can be summarized as follows:

1. The language is built on expressions with identifiers in a path to access a semi-structured data value.
2. Data processing is defined through compositional expressions built on top of basic expressions.
3. The output is defined by a template that specifies how to project computed expressions to a user-defined output.
4. The semantics of a specification define a set of values of identifiers instantiated with valid values and expressions calculated with the instantiated identifiers.
5. The final output is generated by populating templates with the calculated expressions.

Overall, Kiwilang will provide a powerful tool for domain experts to easily specify and maintain their data processing logic, enabling the creation of valuable insights from collected data in various areas such as CYBER ASSET ATTACK SURFACE MANAGEMENT (CAASM), Zero Trust analytics, and threat hunting.
