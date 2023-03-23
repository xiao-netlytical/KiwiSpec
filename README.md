# kiwilang
kiwilang (Knowledge Interpreter With Intelligence) is a project aimed at developing a declarative programming language for documenting data processing by specifying relationships and transformations as code based on semi-structured data in JSON format. It was originally developed to specify the data processing for CAASM and security rules, with the goal of allowing people with a security background to document their expertise with minimal programming involved and quickly incorporate their knowledge into a product. The language is designed to be easy to adopt, read, understand, and maintain.

The initial implementation is based on Python for semi-structured data in JSON format. Under the kiwilang project, several sub-projects have been developed.

1. kiwilang and interpreter
The key building blocks of the language are identifiers, expressions, and relationship operators. The following two examples provide a quick preview of the language.

The first example uses conn.log from Zeek to generate a list of the top 5 DNS initiators for every 5 minutes interval.

    READ conn.json AS flows
    VAR i 
    SELECT
        flows[i]["id.orig_h"] AS dns_src;
        int(epoch_time(flows[i]["ts"])/300) AS window_start;
        SUM(count_one(i)) GROUP BY dns_src,window_start AS dns_requests;
        WHERE flows[i]["id.resp_p"] == 53;
        ORDER BY dns_requests DESC
    CREATE {window_start: [{dns_src: dns_requests} LIMITED 10]}  AS result
    WRITE top_dns_sender.json FROM result

The second example is a fun coding challenge used to explore the language. The problem is to determine if there is a subset of a given set of non-negative integers that adds up to a given sum.

    VAR i
    SELECT
        COLLECT(int_set[i]) AS r_set;  WHERE sum(r_set) == total
    CREATE [r_set] AS result

For more details on Kiwilang, please refer to the Kiwilang directory. 
For additional examples, please see the rules directory.


2. CAASM (Cyber Asset Attack Surface Management) Rules in Kiwilang:

The CAASM directory is intended to include rules for identifying applications, discovering relationships between application servers, and recognizing various patterns and aggregations related to workload, application, and relationships. Currently, the collected rules are limited to using conn.log data collected by Zeek as input.
You can find the files containing collections of rules under the directory "rules/application".

3. Security Rules in KiwiLang

The security rules are designed to identify potential security threats or suspicious activity from the logs. Currently, there are two example rules available for identifying top requests and top DNS requests during each interval, based on the conn.log data collected by Zeek. These rules can be found in the 'rules/security' directory.

4. Interview Question Coding in KiwiLang (For Fun)

Kiwilang was initially developed as a declarative approach for data processing and transformation, specifically for logs and configurations. To further explore the possibilities and limitations of KiwiLang, coding in KiwiLang to solve different kinds of interview questions has become a fun experimental project on the side.

Currently, the KiwiLang interpreter cannot fully support the specifications required for this experiment. 
The code to solve interview problems written in KiwiLang can be found under the 'fun_coding' directory.

5. Working with Codex

There are two sub-interests related to using KiwiLang with code generation from Codex:

    . Using Codex to generate target code in languages such as Python, C, etc., from declararive specifications written in kiwiLang.

    . Using Codex to generate kiwiLang code from natural language descriptions.
    
As a declarative language, kiwiLang is closely resembles natural language with accurate semantics. It is an effective way to document a task or an algorithm using human-like language. Specifications written in kiwiLang are easy to adopt, read, maintain, and are unambiguous. Generating target code from kiwiLang specifications can be a solution for a range of problems.

Although the recent OpenAI Codex model can generate Python, C, SQL, and other code from specifications, it still requires understanding and modifications. Instead of generated code in Python or C code, Code in KiwiLang would be closer to the original request and easier to understand.

This projects involve experiment with Codex to fine-tune the model or prompt engineering for kiwilang, with the goal of generating code in KiwiLang from natural language or generating a target code from kiwiLang.

6. To try kiwilang with the rules and sample data of Zeek log
   git clone kiwi
   cd kiwilang
   python3 kiwi_main.py ../rules/caasm/asset.kiwi
   python3 kiwi_main.py ../rules/security/security.kiwi
   python3 kiwi_main.py ../rules/caasm/asset.kiwi

   the result files are under sample_data/result

7. Future Work:

Our plans for the future include:

    . Collecting more rules for different kinds of data sources
    . Further enhancing the language and improving performance
    . Building a platform to manage rules plug_ins with scheduled jobs
    . Mangaging resuts and developing graphical displays and reports

