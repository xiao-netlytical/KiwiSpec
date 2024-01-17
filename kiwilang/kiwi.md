
# KiwiSpec: A Declarative Approach to Semi-Structured Data Processing

xiao-netlytical@gmail.com

## Description:

KiwiSpec is a project designed to provide a method for specifying data processing logic in a declarative manner. The solution aims to offer both a language and a generic platform for specifying, managing, and executing data processing logic within the KiwiSpec framework. The data under management adopts a semi-structured JSON format, enhancing its applicability across diverse use cases. Key aspects of data processing include search and retrieval operations with filters, data aggregation, correlation, transformation, global logic matching, recursive matching, and the generation of trending reports.

To construct a specification for processing semi-structured data, KiwiSpec utilizes expressions with identifiers representing possible instantiations in a path to access semi-structured data values. Additionally, KiwiSpec provides operators to create more complex computational expressions with conditional logic, aggregation, limiting, and sorting. Together, the declarative language and the specification include constructs for building expressions, specifying data input, creating output templates, and defining output pipelines. With templates to specify the output formats, intricate logic can be implemented by correlating and chaining the data processing results from multiple kiwispecs.

Beyond the language aspect, the KiwiSpec platform also aims to serve as a generic platform for managing, translating, and executing specifications, as well as handling and displaying outputs.

Furthermore, KiwiSpec can also be used as an extension to any imperative language. By embedding the declarative specification for data processing into Python code, the data processing logic can be translated to Python code and executed with the rest of the code.

## Background:

The KiwiSpec project was conceived to provide a specification language that can document the data processing logic for applications in areas such as Cyber Asset Attack Surface Management (CAASM), Zero Trust analytics, and threat hunting.

In these applications, the processing of log data and metadata plays a critical role in deriving valuable insights. Products developed in these areas provide users with functionalities to identify critical assets, understand the relationships between workloads and application servers, detect violations, and surface risk factors from traffic logs, configurations, installations, and upgrade logs.

Creating such applications requires domain expertise to produce valuable insights from the collected data, and the system needs to be kept updated with new learnings. The KiwiSpec project aims to address these needs by providing a language that enables domain experts to document their knowledge and rules easyily, as well as a generic platform capable of managing and interpreting those knowledge and applying them to the collected data.

The applications in the interested areas have common requirements in terms of data processing. The desired commonality of data processing includes retrieving, searching, filtering, transforming, aggregating, correlating, recursive computing, and trending.

In detail, the data processings can be defined as:

• Searching and retrieving: Select matching data as output from multiple inputs.

• Searching with filtering: Select matching data that meets condition computations as output from multiple inputs.

• Transformation: From the selected data, generate output after recomputing.

• Aggregation: Collect a set of data or distinct set of data, calculate sum, count, count distinct, min, max, mean, all, any, and states grouped by some values.

• Extended aggregation: Collect a set of data or distinct set of data based on computing relationships recursively.

• Correlation: Correlate data entries within the same input or multiple inputs.

• Global logic computation: Compute logic expression from multiple collective data entries.

• Trending: Interval-based aggregation or state calculation with changing or trending reports.

## Specification and Language:

The KiwiSpec project aims to provide domain experts with a declarative language and platform to describe their data processing logic in an easily adoptable, readable, writable, and maintainable manner. The platform is designed to facilitate fast building and turnaround time with new security learnings.

The declarative specification and language should allow domain experts to:

. Specify input data in semi-structured format from any storage of memory, file, cloud storage, and/or database.

. Focus on the specification of the data transformation from input to output.

. Focus on describing data processing rules and logic.

. Use a simple and rich language to specify the needed data processing.

. Use a language that is easy to adopt and understand.

. Write specifications that are easy to read and maintain.


As a declarative language and platform, the language and specification of KiwiSpec should provide clear ways to specify the source of input data, data filtering and computation logic, output format, and target output storage. KiwiSpec achieves this through five main constructs used to build a declarative specification:

• READ: For reading input data from various sources such as memory, file, cloud storage, and/or database.

• SELECT with condition, sorting, and limiting: For specifying data processing logic, this construct enables users to select and filter data from multiple inputs, transform the data, aggregate and correlate the data, perform recursive computation, evaluate composite logic expression and generate trending reports.

• CREATE: For building output data structures. This clause enables users to create data structures that are needed for the output.

• UPDATE: For modifying existing or output data structures. This clause enables users to update data structures that are needed for the output.

• WRITE: For writing output to targets such as memory, file, cloud storage, and/or database.

## Expression and Language:

The fundamental building block of KiwiSpec is expressions with identifiers. A basic expression is a path expression with identifiers representing keys and indexes in a semi-structured data path to access a data value. To build more complex logic, Compositional expressions are introduced. Compositional expressions can be composed from basic or compositional expressions using operators including COLLECT, COLLECT DISTINCT, COLLECT EVAL, GROUP BY, EXTEND BY, ORDER BY, WHERE, CASE/END, LIMIT, SUM, COUNT, COUNT DISTINCT, MIN, MAX, MEAN, ALL, and ANY. Python expressions are also valid expressions. With these operators, expressions can describe the logic for searching with filtering, math and logic computation, aggregation, correlation, transformation, composite logic matching and recursive computations. 

With identifiers as placeholders for all the possible instatiations, the declarative language allows users to focus on describing data processing and transformation as expressions, without worrying about walking and manipulating data structures step-by-step.

Expressions can comprise paths accessing data values from multiple data structures. The same identifiers can be used to access the same instance with further extensions to different levels of the data structures. An expression accessing a value from one data structure can be used in a path to access another data structure. In these ways, multiple data sources are correlated. The WHERE operator can also be used to correlate multiple data entries or data sources by specifying the relationships between expressions. Different identifiers accessing the same data path represent different instantiations which can be used to create a correlation between the entries. Relationship definition between entries can be used to build a recursive chain. EXTEND BY operator is used to describe those relationships. 

A composite logic expression comprises multiple logic units, where the evaluation involves utilizing multiple instances from a dataset. Each instance is independently applied to fulfill any logic unit until the composite expression is satisfied. Some logic expressions related to asset management and security fall into this category. To facilitate the evaluation of composite logic expressions, COLLECT EVAL is introduced. It is passed a composite logic definition along with expressions containing identifiers. The calculated instances from these expressions are used to independently evaluate each logic unit until the collected result aligns with the defined logic.

An expression calculated as a true or false value with identifier instantiated can serve as a condition expression. An expression can be followed by a condition keyword and a condition expression to form a compositional expression. An expression with an aggregation operator COLLECT, COLLECT DISTINCT, SUM, COUNT, COUNT DISTINCT, ANY, ALL, MIN, MAX, or MEAN forms an aggregation expression. An aggregation expression can be followed with GROUP BY and ORDER BY keyword with an expression or identifier names. Expression build from COLLECT operator will generate a set with or without unique values. An aggregation expression generating a set value as a result can be followed by an ORDER BY keyword to define the order of a set. Multiple expressions with condition operators can be grouped together by CASE operator to form a multi-choice expression.

KiwiSpec borrows several keywords from SQL, including SELECT, WHERE, AS, GROUP BY, and ORDER BY, because they are widely adopted and self-explanatory. In SQL, the SELECT clause serves as the imperative procedure for obtaining table row instantiations. In KiwiSpec, however, users have more freedom with expressions and identifiers, and the underlying procedures allows any instantiation of identifiers with the calculated expressions. In this way, KiwiSpec offers a more flexibility to specify data manipulation, while still drawing upon familiar and widely used keywords.

In this example, KiwiSpec allows users to specify identifier variables i and j and then select data[i].interest and data[j].interest, where the condition data[i].interest == data[j].interest is true.

    VAR i, j SELECT data[i].interes; data[j].interes; where data[i].interes == data[j].interes

A KiwiSpec specification is made from the constructs of READ, SELECT, WITH, CREATE, and WRITE.

Expressions specified with SELECT clause are assigned a name with AS or FROM keywords. Expression names can be referred by other expressions or output templates. 

Within the SELECT construct, the WHERE, GROUP BY or ORDER BY clauses can be used as a separate clause to apply the clause to all the expressions globally.

A KiwiSpec specification can include a READ construct to specify data sources from a file, storage, a data structure name, or a database.

A kewilang specification can include a WITH clauses to pipeline an output of a specification to an input of another specification.

A kewilang specification can include a WRITE construct to specify an output to a file, a storage, a data structure name, or in a database.


## Output Template, Semantics, and Result Generation:

KiwiSpec provides a CREATE construct that allows users to build outputs from expressions. The CREATE construct and clause use templates to define the outputs, which specify how to project the calculated expressions and identifiers as desired by the user. The templates are in semi-structured format and built from expression names and identifier names assigned by the SELECT clause. The AS keyword binds an expression to an expression name, while the FROM keyword declares an identifier name. All the expressions and identifiers referred by a template are grouped together to form an expression tuple.

The algorithm to generate final outputs from KiwiSpec specifications involves two calculation phases.

The first phase is Identifier Instantiation, Expression Calculation, and Tuple Materialization. 

By instantiating identifiers with valid values, expressions are materialized. A valid tuple value is formed by valid identifier instantiations and valid expression calculations which satisfy the condition clauses. The resulting tuple set is a non-redundant set of all the valid tuple values.

The second phase of the computation is output projection. The final outputs are defined by one or more templates specified in a CREATE clause. Each template specifies how the output should be projected from the resulting tuple set. Since the resulting tuple includes the collection of referred expressions names and identifiers, the template can be populated by each tuple value. The whole output set is generated by appending each population of the template.

An interpreter is implemented to convert a specification to executable code. The translated Python code, for example, will execute the above semantics and algorithm. The KiwiSpec interpreter also combines, pipelines, and optimizes the loops with the instantiation and calculation to achieve the best performance.

As a complete solution, a platform is also under development to manage specifications, data sources, and outputs. The platform will provide an interface for loading the specifications and scheduling executions.

## Language Definition

Syntax:

lowercase          := [a-z]
uppercase          := [A-Z]
letter             := lowercase | uppercase
digit              := [0-9]

name := letter, {letter | digit | "_" letter | "_" digit}
var := letter, {letter | digit}

path_name := name

file_path := {path_name,"/"}, path_name

kiwi_expr := (name, {"[", (var | name | kiwi_expr | "_"),  ["|", name] "]"}) | (var, "FROM", kiwi_expr)

kiwi_composite_expr := ("SELECT SET" | "SELECT LIST" | "COUNT DISTINCT" | "SUM" | "MAX" | "MIN"),
 "(", (kiwi_expr, {"|",  kiwi_expr}, ")"

list_template := "[", (var | name), {",", (var | name)}, "]" 

dictionary_template := "{", (name,":", var), {",", (name, ":", var)}, "]" 

create_template :=  name | list_template | dictionary_template |
           "{", (name,":", list_template), {"," ,(name,":", list_template)}, "}" |
           "[", dictionary_template, "]"

define_clause := "DEFINE", (path_name, "=", file_path), {",", (path_name, "=", file_path) }

group_by_clause := "GROUP BY", (name|"NONE"), {",", name}

extend_by_clause := "EXTEND BY", name | "(", name, {",", name}, ")"

where_clause := "WHERE", (condition_ex | logic_ex), {";", (condition_ex | logic_ex)}

order_by_clause := "ORDER BY", name, ["DEST"], ["LIMIT", digit], "FOR", name,  {";", name, ["DEST"], ["LIMIT", digit], "FOR", name}

as_clause := kiwi_expr, ["WHERE", (condition_ex | logic_ex)], "AS", name

composite_as_clause := kiwi_composite_expr, ["WHERE", (condition_ex | logic_ex)], [group_by_clause] "AS", name

extend_as_clause := "SELECT SET", ["WHERE", (condition_ex | logic_ex)], [extend_by_clause] "AS", name

logic_expr_1 := "(", (name|logic_expr_1|logic_expr_2),  ("AND" | "OR"),  (name|logic_expr_1|logic_expr_2), ")"
logic_expr_2 := (name|logic_expr_1|logic_expr_2),  ("AND" | "OR"),  (name|logic_expr_1|logic_expr_2)

logic_unit_1 := "(", "UNIT", "(", logic_expr_1 | logic_expr_2, ")", 
                 {("AND" | "OR"), "UNIT", "(", logic_expr_1 | logic_expr_2, ")"}, ")"

logic_unit_2 := "UNIT", "(", logic_expr_1 | logic_expr_2, ")", 
                 {("AND" | "OR"), "UNIT", "(", logic_expr_1 | logic_expr_2, ")"}

unit_logic_string := (logic_unit_1 | logic_unit_2), { ("AND" | "OR"), (logic_unit_1 | logic_unit_2) }

eval_as_clause := "COLLECT EVAL", "(", (kiwi_expr | unit_logic_string), {name, "=", name}, ")", "AS", name

read_statement := "READ", (path_name|file_path), "AS", name, {";", (path_name|file_path), "AS", name}

write_statement := "WRITE", (path_name|file_path), "FROM", name, {";", (path_name|file_path), "FROM", name}

kiwispec :=

    [define_clause],
    [read_statement],

    "CREATE", create_template, "AS", name, {";", create_template, "AS", name},

    "VAR", var, {",", var},
    
    "SELECT", ":",
        (as_clause|composite_as_clause|extend_as_clause|eval_as_clause), 
        ";", {(as_clause|composite_as_clause|extend_as_clause|eval_as_clause), ";"},
        
    [group_by_clause],
    [where_clause],
    [order_by_clause],

    [write_statement],


### SELECT statement and Expressions:

SELECT statement is the main component of a wikispec.

The SELECT statement specifies a set of expressions with multiple variables to access various json data structures and assigns the expressions with names. Expressions defines a set of transformed values. By iterating through valid variable instantiations, calculated results from expressions are organized as a set of value tuples.

Syntax:

    select :=
        "VAR", var, {",", var},
        
        "SELECT", ":",
            (as_clause|composite_as_clause|extend_as_clause|eval_as_clause), 
            ";", {(as_clause|composite_as_clause|extend_as_clause|eval_as_clause), ";"},
            
        [group_by_clause],
        [where_clause],
        [order_by_clause],

"SELECT" statement includes three sections.

In the main section, expressions are specified and bound to an expression name using 'AS.'

In the second section, conditions and grouping can be defined globally and applied to all the expressions inside a select statement.

In the third section, the 'ORDER BY' and 'LIMIT' can be applied to control the output of the calculated results.

Expressions within SELECT can take the form of path expressions or compositional expressions built from path expressions and other compositional expressions. Operations supported by Python for building an expression are also supported by KiwiSpec. Additionally, KiwiSpec defines a set of operations to build compositional expression.

An expression can only refer the names which already defined in the previous expression assignment. 


### VAR clause:

Syntax:

    var := "VAR", var, {",", var}


The 'var' clause declares a set of identifiers.

An identifier is a key variable or an index variable that serves as a placeholder in a path for accessing a semi-structured value. An expression with variables in the path is referred to as a path expression. Such a path expression defines a set of values calculated through valid variable instantiations.

"_" can be used as any variable without a declaration.


### AS clause:

Syntax:

    as := (as_clause|composite_as_clause|extend_as_clause|eval_as_clause), 
        ";", {(as_clause|composite_as_clause|extend_as_clause|eval_as_clause), ";"}

"AS" clause binds an expression to an expression name. Once an expression name is defined, it can be used in the following value expressions, condition expressions and output template.


The left of AS is an expression, the right of AS is the bound expression name.

#### "|" operator in a path to access a json value:

Syntax:

    kiwi_expr := name, {"[", (var | name | kiwi_expr | "_"),  ["|", name] "]"}

A key or index in an expression can be followed with "|" to set a default value.

When calculating an expression, the generated key or index may be out of range or an invalid access. By default kiwispec will guarantee to only involve valid keys, indexes and values. But user can also define a default value when a invalid key, index or value is generated. 

Example:
    e["text" | "default text "]
    a[b[i] | "default value"]

#### index_by function:

    index_by(expression) is a wikispec function, which returns the next index for a generated value.

### FROM clause:

Syntax:

    var, "FROM", kiwi_expr

FROM operator declares a variable as a key or index identifier for a specific json structure.
With FROM clause an expression is specified and the valid instantiations defines the value set.

### COLLECT SET:

Syntax:

    kiwi_composite_expr := ("SELECT SET" | "SELECT LIST" | "COUNT DISTINCT" | "SUM" | "MAX" | "MIN"),
    "(", (kiwi_expr, {"|",  kiwi_expr}, ")"
    group_by_clause := "GROUP BY", name, {",", name}
    composite_as_clause := kiwi_composite_expr, ["WHERE", (condition_ex | logic_ex)], [group_by_clause] "AS", name

COLLECT SET is a KiwiSpec operator employed to construct composite expressions.

'COLLECT SET' creates a new expression from the input expressions. An expression specified by 'COLLECT SET' defines a set of lists, each corresponding to a 'group by' group. The values in each list are non-redundant unions of calculated values from the input expressions, achieved by iterating through relevant variable  instantiations associated with the grouping.

A 'WHERE' clause following the COLLECT operator specifies the necessary calculation conditions.

A 'GROUP BY' clause following the COLLECT operator defines the grouping criteria with parameters specified by identifiers and expression names.

If 'GROUP BY' is not present and not defined globally, all non-aggregated parameters are utilized as the grouping parameters.

The option of using 'None' as a parameter indicates no specific grouping.

### COLLECT LIST:

Syntax:

    kiwi_composite_expr := ("SELECT SET" | "SELECT LIST" | "COUNT DISTINCT" | "SUM" | "MAX" | "MIN"),
    "(", (kiwi_expr, {"|",  kiwi_expr}, ")"
    group_by_clause := "GROUP BY", name, {",", name}
    composite_as_clause := kiwi_composite_expr, ["WHERE", (condition_ex | logic_ex)], [group_by_clause] "AS", name

COLLECT LIST is a KiwiSpec operator employed to construct composite expressions.

'COLLECT LIST' creates a new expression from the input expressions. An expression specified by 'COLLECT LIST' defines a set of lists, each corresponding to a 'group by' group. The values in each list are unions of calculated values from the input expressions, achieved by iterating through relevant variable instantiations associated with the grouping.

A 'WHERE' clause following the COLLECT operator specifies the necessary calculation conditions.

A 'GROUP BY' clause following the COLLECT operator defines the grouping criteria with parameters specified by identifiers and expression names.

If 'GROUP BY' is not present and not defined globally, all non-aggregated parameters are utilized as the grouping parameters.

The option of using 'None' as a parameter indicates no specific grouping.

### COUNT DISTINCT:

Syntax:

    kiwi_composite_expr := ("SELECT SET" | "SELECT LIST" | "COUNT DISTINCT" | "SUM" | "MAX" | "MIN"),
    "(", (kiwi_expr, {"|",  kiwi_expr}, ")"
    group_by_clause := "GROUP BY", name, {",", name}
    composite_as_clause := kiwi_composite_expr, ["WHERE", (condition_ex | logic_ex)], [group_by_clause] "AS", name

COUNT DISTINCT is a KiwiSpec operator employed to construct composite expressions.

'COUNT DISTINCT' creates a new expression from the input expressions. An expression specified by 'COUNT DISTINCT' defines a value for each 'group by' group. The value represents the total count of distinct values obtained from the union of calculated expressions, achieved by iterating through relevant variable instantiations associated with the group.

A 'WHERE' clause following the COLLECT operator specifies the necessary calculation conditions.

A 'GROUP BY' clause following the COLLECT operator defines the grouping criteria with parameters specified by identifiers and expression names.

If 'GROUP BY' is not present and not defined globally, all non-aggregated parameters are utilized as the grouping parameters.

The option of using 'None' as a parameter indicates no specific grouping.

### SUM:

Syntax:

    kiwi_composite_expr := ("SELECT SET" | "SELECT LIST" | "COUNT DISTINCT" | "SUM" | "MAX" | "MIN"),
    "(", (kiwi_expr, {"|",  kiwi_expr}, ")"
    group_by_clause := "GROUP BY", name, {",", name}
    composite_as_clause := kiwi_composite_expr, ["WHERE", (condition_ex | logic_ex)], [group_by_clause] "AS", name
SUN is a KiwiSpec operator employed to construct composite expressions.

'SUM' create a new expression from the input expression. An expression specified by 'SUM' defines a value for each 'group by' group. The value represents the sum of calculated values from the input expressions, achieved by iterating through relevant variable instantiations associated with the group.

A 'WHERE' clause following the COLLECT operator specifies the necessary calculation conditions.

A 'GROUP BY' clause following the COLLECT operator defines the grouping criteria with parameters specified by identifiers and expression names.

If 'GROUP BY' is not present and not defined globally, all non-aggregated parameters are utilized as the grouping parameters.

The option of using 'None' as a parameter indicates no specific grouping.

### MIN:

Syntax:

    kiwi_composite_expr := ("SELECT SET" | "SELECT LIST" | "COUNT DISTINCT" | "SUM" | "MAX" | "MIN"),
    "(", (kiwi_expr, {"|",  kiwi_expr}, ")"
    group_by_clause := "GROUP BY", name, {",", name}
    composite_as_clause := kiwi_composite_expr, ["WHERE", (condition_ex | logic_ex)], [group_by_clause] "AS", name

MIN is a KiwiSpec operator employed to construct composite expressions.

'MIN' create a new expression from the input expressions. An expression specified by 'MIN' defines a value for each 'group by' group. The value represents the minimal value obtained from the union of calculated expressions, achieved by iterating through relevant variable instantiations associated with the group.

A 'WHERE' clause following the COLLECT operator specifies the necessary calculation conditions.

A 'GROUP BY' clause following the COLLECT operator defines the grouping criteria with parameters specified by identifiers and expression names.

If 'GROUP BY' is not present and not defined globally, all non-aggregated parameters are utilized as the grouping parameters.

The option of using 'None' as a parameter indicates no specific grouping.

### MAX:

Syntax:

    kiwi_composite_expr := ("SELECT SET" | "SELECT LIST" | "COUNT DISTINCT" | "SUM" | "MAX" | "MIN"),
    "(", (kiwi_expr, {"|",  kiwi_expr}, ")"
    group_by_clause := "GROUP BY", name, {",", name}
    composite_as_clause := kiwi_composite_expr, ["WHERE", (condition_ex | logic_ex)], [group_by_clause] "AS", name

MAN is a KiwiSpec operator employed to construct composite expressions.

'MAX' create a new expression from the input expressions. An expression specified by 'MAX' defines a value for each 'group by' group. The value represents the maxima value obtained from the union of calculated expressions, achieved by iterating through relevant variable instantiations associated with the group.

A 'WHERE' clause following the COLLECT operator specifies the necessary calculation conditions.

A 'GROUP BY' clause following the COLLECT operator defines the grouping criteria with parameters specified by identifiers and expression names.

If 'GROUP BY' is not present and not defined globally, all non-aggregated parameters are utilized as the grouping parameters.

The option of using 'None' as a parameter indicates no specific grouping.

### GROUP BY Clause:

Syntax:

    group_by_clause := "GROUP BY", (name|"NONE"), {",", name}

where name can be an identifier or an expression name, or NONE.

The GROUP BY clause specifies a set of calculated values for the aggregation clause to organize the calculation results. This clause can be defined either globally or after an expression.


### EXTEND BY Clause:

Syntax:

    extend_by_clause := "EXTEND BY", (name | "(", name, {",", name}, ")")

    extend_as_clause := "SELECT SET","(",  (name | "(", name, {",", name}, ")"), ")", ["WHERE", (condition_ex | logic_ex)], [extend_by_clause] "AS", name

where an expression name or a tuple of expression names is used as the building blocks.
Lets use EX to represent the selected name or tuple, EY to represent the extened name or tuple.

The EXTEND BY clause defines a set of lists. Each list is extended by the value calculated from EY, achieved through iterative evaluation of conditions between the instantiated EY and EX, where the instantiated EX value is a member of the list. If no such list exists, the EY value forms an initial list.


### COLLECT EVAL and Logic UNIT: 

COLLECT EVAL is introduced to evaluate composite logic expressions. These composite logic expressions consist of multiple logic units, where the evaluation involves different instantiations for each logic unit. Each logic unit is evaluated independently using a set of instantiations until the composite expression is satisfied.

Syntax:

    logic_expr_1 := "(", (name|logic_expr_1|logic_expr_2),  ("AND" | "OR"),  (name|logic_expr_1|logic_expr_2), ")"
    logic_expr_2 := (name|logic_expr_1|logic_expr_2),  ("AND" | "OR"),  (name|logic_expr_1|logic_expr_2)

    logic_unit_1 := "(", "UNIT", "(", logic_expr_1 | logic_expr_2, ")", 
                    {("AND" | "OR"), "UNIT", "(", logic_expr_1 | logic_expr_2, ")"}, ")"

    logic_unit_2 := "UNIT", "(", logic_expr_1 | logic_expr_2, ")", 
                    {("AND" | "OR"), "UNIT", "(", logic_expr_1 | logic_expr_2, ")"}

    unit_logic_string := (logic_unit_1 | logic_unit_2), { ("AND" | "OR"), (logic_unit_1 | logic_unit_2) }

    eval_as_clause := "COLLECT EVAL", "(", (kiwi_expr | unit_logic_string), {name, "=", name}, ")", "AS", name

Example:

    COLLECT EVAL(gl_ex | gl_e, v1 = p1, v2 = p2, ...) AS gc

where gl_ex is an expresion which will create a composite logic string after instantiation.
gl_ex is a composite logic string.
v1, v2, ... are variables refered in the Composite logic definition.
P1, P2, ... are expressions, the calculated instantiation results will be passed in as parameters for Composite logic evaluation.  

The aggregated logic result from multiple evaluations of the logic unit will be assigned to gc.

### WHERE clause:

Syntax:

   where_clause := "WHERE", (condition_ex | logic_ex), {";", (condition_ex | logic_ex)}

where (condition_ex | logic_ex) are condition expressions evaluated as TRUE or FALSE.
The WHERE clause can be defined either globally or after an expression to specify the necessary conditions to calculate expressions.


### ORDER BY Clause:

Syntax:

    order_by_clause := "ORDER BY", name, ["DEST"], ["LIMIT", digit], "FOR", name,  {";", name, ["DEST"], ["LIMIT", digit], "FOR", name}

The ORDER BY clause specifies the sorting order based on the expression name for the generated result tuple, which is derived from the calculated expressions for each result template.

### LIMIT Clause:

Syntax:

    order_by_clause := "ORDER BY", name, ["DEST"], ["LIMIT", digit], "FOR", name,  {";", name, ["DEST"], ["LIMIT", digit], "FOR", name}

The LIMIT keyword sets limit for the generated result tuple, which is derived from the calculated expressions for each result template.

### CREATE Statement:
 
Syntax:

    list_template := "[", (var | name), {",", (var | name)}, "]" 

    dictionary_template := "{", (name,":", var), {",", (name, ":", var)}, "]" 

    create_template :=  name | list_template | dictionary_template |
            "{", (name,":", list_template), {"," ,(name,":", list_template)}, "}" |
            "[", dictionary_template, "]"
 

The `CREATE` statement defines output formats using templates, with each template assigned a unique name. The output is generated by populating the templates with value tuples calculated from the `SELECT` statement.

### UPDATE Statement:

Syntax:

    update_kiwi_expr := (name, {"[", (var | name | update_kiwi_expr )"]"})
    update_as_clause := update_kiwi_expr, ["WHERE", (condition_ex | logic_ex)], "AS", update_kiwi_expr

    update := "UPDATE",
        "VAR", var, {",", var},
            
        "SET", ":",
            update_as_clause, ";", {update_as_clause ";"},
            [where_clause]


where var represents variables acting as placeholders for keys or indices in a JSON structure.
The UPDATE statement defines how to modify a JSON structure.

By iterating through instantiations of the variables, the left-hand side of the expression is assigned the value of the corresponding right instantiation, provided that the conditions specified in the condition expression are met.

### DEFINE:

Syntax:

    define_clause := "DEFINE", (path_name, "=", file_path), {",", (path_name, "=", file_path) }


The DEFINE clause defines a set of path names using "=", where these path names can be used by READ and WRITE statement for reading and writing files from the specified directory paths

### READ Statement:

Syntax:

    read_statement := "READ", (path_name|file_path), "AS", name, {";", (path_name|file_path), "AS", name}

At the beginning of a Kiwispec, following the `DEFINE` clause, the `READ` statement reads data structures from files and binds the structures to variables using the `AS` keyword.

### WRITE Statement:

Syntax:

    write_statement := "WRITE", (path_name|file_path), "FROM", name, {";", (path_name|file_path), "FROM", name}

At the end of a Kiwispec, the `WRITE` statement writes results from the `CREATE` statement to files.

## Examples:

The following is a list of examples of data processing specifications in the applications of CAASM, risk analysis, and threat hunting. These specifications are written in KiwiSpec and use JSON format for input and output data structures.

The input files are JSON files that are converted from the conn.log generated by Zeek. 
Each log entry in the conn.log contains the following fields:

id.resp_h  - destination IP of a connection

id.orig_h   - source IP of a connection

orig_pkts  - packet count from source to destination

resp_pkts - packet count from destination to source

proto        -  protocol of a connection

id.resp_p -  destination port 

ts             - connection starting time 

### Example 1:

In this example, the following specification describes the data processing for collecting all the IP addresses that are either the source or destination IP in the conn.json file.

                
        READ conn.json AS flows
        CREATE ips AS r
        VAR i
        SELECT
            COLLECT SET(flows[i]["id.resp_h"]  |  flows[i]["id.orig_h"]) AS ips
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


### Example 2:

In this example, the following specification describes the data processing of aggregating connections between a source and a destination. For each source and destination pair, packet counts of sending and receiving are added up. Protocol:ports are aggregated as a list, and a total flow number is counted.

        READ conn.json AS flows
        CREATE  
            [{"src":s_ip, "dst":d_ip, "o_pkts_ct":o_pkts, "r_pkts_ct":r_pkts, "service":proto,"flows": count}] AS result
        VAR  i 
        SELECT
            flows[i]["id.orig_h"] AS s_ip;
            flows[i]["id.resp_h"] AS d_ip;
            SUM(flows[i]["orig_pkts" | 0]) AS o_pkts;
            SUM(flows[i]["resp_pkts" | 0]) AS r_pkts; 
            count distinct(i)  AS count;
            COLLECT SET(flows[i]["proto"]+":"+str(flows[i]["id.resp_p"])) AS proto
        WRITE  traffic_agg.json FROM result

In the specification above:

•	By default, aggregation will be grouped by all the non aggregating expressions in the result.

•	In this example, aggregations are grouped by (s_ip, d_ip) by default.

•	VAR i: used as an identifier to access a connection entry flow[i].

•	SUM: sum of flows[i]["orig_pkts”] if flows[i] has field "orig_pkts”.

•	flows[i]["orig_pkts” |  0]: If a flow entry does not have field “orig_pkts” or“"resp_pkts” field, 0 will be  used instead.

•	flows[i]["proto”]+”:”+str(flows[i]["id.resp_p”]): string concatenation.

•	SELECT .. AS .. : define a set of expressions and assign a name to an expression.

•	CREATE: define the output as a list of dictionaries, each dictionary is populated by a valid expressions tuple, the result dictionary is added to the list.

### Example 3:

In this example,  the following specification describes the data processing of getting the top 10 IPs which initiate the most distinct outbound requests. 
Using a log file generated by Zeek as input,  the number of distinct outbound request of per protocol:port from a source IP is counted. In addition, the total packet and byte count for each source IP are also collected.
The final output is a sorted list of the top 10 dictionaries, with each dictionary containing information about the source IP, packet count, byte count, and service count. The output is also written to the "top_out_rel.json" file.

        READ conn.json AS flows
        CREATE
            [{"ip": source_ip, "pkts": pkts, "bytes":bytes, "out_request": out_request}] AS result
        VAR i 
        SELECT
            flows[i]["id.orig_h"] AS source_ip;
            COUNT DISTINCT(flows[i]["proto"]+":"+str(flows[i]["id.resp_p"])) AS out_request;
            SUM(flows[i]["orig_pkts" | 0] + flows[i]["resp_pkts" | 0]) AS pkts;
            SUM(flows[i]["orig_bytes" | 0] + flows[i]["resp_bytes" | 0]) AS bytes;
        ORDER BY out_request DESC LIMIT 10
        WRITE top_out_rel.json FROM result

In the specification above:

•	COUNT DISTINCT: counts the total number of distinct proto:port aggregated by a source IP.

•	ORDER BY:  the result tuples are ordered by the out_request count.

•	LIMIT:  the output list is limited to the first 10 dictionaries.

### Example 4:

In these examples, the following specifications describe the data processing to identify a destination IP as an application server. The classification of an application server is based on its inbound and outbound protocol and port with the logic defined in a json structure - application, the protocol and port are obtained from connection logs generated by Zeek. 

#### 4.1
    # application servers are defined by a list of application name with it's classification logic using composite expression.
    application =
    [
        {
            "app_name":"AAAserver", 
            "lookup_condition": "unit (proto==\"udp\" and 1800<=port<=1812) and unit(proto==\"udp\" and port==1813) or unit(proto ==\"udp\" and port==1416) and unit(proto==\"udp\" and port==1415)"
        },
        {
            "app_name": "Splunk", 
            "lookup_condition":  "unit (proto == \"tcp\" and port == 1812) and (unit(proto == \"tcp\" and port == 80) or  unit(proto == \"tcp\" and port == 443) or unit(proto == \"tcp\" and port == 8000) or unit(proto == \"tcp\" and port == 8089)) and unit(out_proto == \"tcp\" and out_port == 9997) and  unit(out_proto == \"tcp\" and out_port == 8089)"
        },
        {
            "app_name": "DNSserver", 
            "lookup_condition": "unit (proto == \"tcp\" and port == 53) or unit(proto == \"udp\" and port == 53)"
        },
        {
            "app_name": "WEBserver", 
            "lookup_condition": "unit (proto == \"tcp\" and port == 80)"
        }
    ]

    # get an ip to it's received proto/port mapping, and an ip to it's sent proto/port mapping
    READ {conn_path}/conn.json AS flows; 
    create {sip:out_port} as ip_out_port; {dip:in_port} as ip_in_port
    var i select
        flows[i]["id.orig_h"] as sip;
        collect set((flows[i]["proto"], flows[i]["id.resp_p"])) group by sip as out_port;
        flows[i]["id.resp_h"] as dip;
        collect set((flows[i]["proto"], flows[i]["id.resp_p"])) group by dip as in_port;
        where flows[i]["conn_state"] in ["OTH", "SF", "S1", "S2", "S3", "RSTO", "RSTR"]

    # apply the application definition one by one with an IP's in proto/port set and out proto/port set.
    # "collect eval" will apply a set of inputs to a composite expression by evaluating the expression unit by unit to get the combined result.
    create {ip:apps} as all_result 
    var ip, k, x, y select 
        ip_in_port[ip] as in_port_set; 
        ip_out_port[ip | []] as out_port_set; 
        collect eval(application[k]["lookup_condition"], proto=in_port_set[x][0], 
                        port = in_port_set[x][1],
                        out_proto = out_port_set[y][0], 
                        out_port = out_port_set[y][1]) as app_condition;
        collect list(application[k]["app_name"]) where app_condition group by ip as apps;

    # filter out undefined IPs and write the final result to ip_apps.json.
    create {i:result} as r
    var i select
        all_result[i] as result;
        where result

    WRITE ip_apps.json from r

#### 4.2
In the following examples, the server_definition.json file defines the required inbound and outbound protocol:ports to classify a server. The classification logic is defined by an user defined API -eval_logic_expr.

In section 4.2.1, the output is defined as a relationship between an IP address and the applications it supports. In section 4.2.2, the output is defined as a relationship between an application and all the IPs associated with it.

#### 4.2.1

        READ conn.json AS flows, application_rule.json AS application
        CREATE {ip1:out_port} AS r_src; {ip2:in_port}  AS r_dst
        VAR i 
        SELECT
            flows[i]["id.orig_h"] AS ip1;
            COLLECT SET(flows[i]["proto"].upper()+"_"+str(flows[i]["id.resp_p"])) GROUP BY ip1 AS out_port;
            flows[i]["id.resp_h"] AS ip2;
            COLLECT SET(flows[i]["proto"].upper()+"_"+str(flows[i]["id.resp_p"])) GROUP BY ip2 AS in_port

        CREATE [{"ip":ip, "server":apps}] AS r 
        VAR ip, k 
        SELECT
            r_dst[ip] AS out_port; 
            r_src[ip | []] AS in_port; 
            COLLECT SET(application[k]["app_name"]) GROUP BY ip AS apps;
        WHERE 
            eval_logic_expr(application[k]["outbound_protocol"], out_port);
            eval_logic_expr(application[k]["inbound_protocol"], in_port)
        WRITE ip_server.json FROM r

#### 4.2.2

        READ conn.json AS flows, application_rule.json AS application
        CREATE {ip1:out_port} AS r_src; {ip2:in_port}  AS r_dst
        VAR i 
        SELECT
            flows[i]["id.orig_h"] AS ip1;
            COLLECT SET(flows[i]["proto"].upper()+"_"+str(flows[i]["id.resp_p"])) GROUP BY ip1 AS out_port;
            flows[i]["id.resp_h"] AS ip2;
            COLLECT SET(flows[i]["proto"].upper()+"_"+str(flows[i]["id.resp_p"])) GROUP BY ip2 AS in_port

        CREATE [{"ip":ips, "server":app}] AS r 
        VAR ip, k 
        SELECT
            r_dst[ip] AS out_port; 
            r_src[ip | []] AS in_port; 
            application[k]["app_name"] AS app;
            COLLECT SET(ip) group by app AS ips;
        WHERE 
            eval_logic_expr(application[k]["outbound_protocol"], out_port);
            eval_logic_expr(application[k]["inbound_protocol"], in_port)
        WRITE server_ip.json FROM r


In the specifications above:

•	The output of one processing logic can be passed on to another processing logic.

### Example 5:

In this example, the following specification describes the data processing for identifying the top 5 DNS initiators in 5-minute intervals. During each interval, the number of DNS requests is tallied for each source IP address. The resulting tuples (window, requesting IP address, and number of requests) are sorted by the number of requests. The final output is a list of the top 5 source IPs with their respective number of requests and 5-minute interval, ranked by the number of requests.

        READ conn.json AS flows
        CREATE {window_start: [{dns_src: dns_requests}]}  AS result
        VAR i 
        SELECT
            flows[i]["id.orig_h"] AS dns_src;
            int(epoch_time(flows[i]["ts"])/300) AS window_start;
            count distinct(i) AS dns_requests;
            WHERE flows[i]["id.resp_p"] == 53;
            ORDER BY dns_requests DESC LIMITED 5
        WRITE top_dns_sender.json FROM result


In the specification above:

•	DNS:  requests are grouped by non-aggregating values: dns_src and window_start.

•	WHERE:  clause filters the flow[i] for DNS requests.

•	ORDER BY: The result tuples are ordered by the number of DNS requests using the ORDER BY clause.

•	LIMIT: For each window, the top 5 source IPs with the highest DNS request count are added to the list using a LIMIT clause.

### Example 6:

In this example, the following specification describes the data processing for identifying the top 10 packet sending ip pairs and top 10 byte sending ip pairs. With separate templates to define each top 10 ip pairs, two tuple sets are generated for each template. The final results are stored in r1 and r2.

        READ read_path AS flows; write_path/ip_to_servers.json AS srv_names
        CREATE [{"src":s_ip, "dst":d_ip, "orig_pkts": orig_pkts}] AS r1 ;
            [{"src":s_ip, "dst":d_ip, "orig_bytes": orig_bytes}] AS r2  
        VAR i SELECT
            flows[i]["id.orig_h"] AS s_ip;
            flows[i]["id.resp_h"] AS d_ip;
            SUM(flows[i]["orig_pkts" | 0]) AS orig_pkts;
            SUM(flows[i]["orig_bytes" | 0]) AS orig_bytes;
            ORDER BY orig_pkts DESC LIMIT 10 FOR r1;  orig_bytes DESC LIMIT 10 FOR r2
        UPDATE VAR i SET
            r1[i]["server"] AS srv_names[r1[i]["src"] | []]

        UPDATE VAR i SET
            r2[i]["server"] AS srv_names[r2[i]["src"] | []]

        WRITE write_path/top_bytes_sender.json FROM r2; 
              write_path/top_pkts_sender.json FROM r1

In the specifications above:

•	UPDATE: updates r1 and r2 by adding the server name of the src address for every entry.

### Example 7:

In this example, the following specification describes the data processing for correlating the top connection/concatenated connection duration with the top bytes sender. This example demonstrates that the result from multiple kiwispec can be utilized to build more complicated data processing logic.

        READ write_path/top_duration.json AS top_dur_ip; 
             write_path/top_bytes_sender.json AS top_byte_ip
        CREATE {s_ip_1: srv} AS r
        VAR i, j SELECT
            top_byte_ip[i]["src"] AS s_ip_1;
            top_byte_ip[i]["server"] AS srv;
            top_dur_ip[j]["src"] AS s_ip_2;
        WHERE s_ip_1 == s_ip_2
        WRITE write_path/top_duration_and_out_byte.json FROM r

In the specifications above:

•	READ: reads in the top duration and the top bytes sender results calculated by previous executions of kiwispecs.

### Example 8:
In this example, the following specification outlines the data processing procedure for gathering connection paths in which the destination of one connection serves as the source of the next connection, given the condition of the protocol being 445.

        READ conn_path/conn.json AS flows; output_path/ip_to_servers.json AS srv
        CREATE   [path_recording] AS result
        VAR i, j SELECT
            flows[i]["id.orig_h"] AS s_ip_1;
            flows[i]["id.resp_h"] AS d_ip_1;
            flows[j]["id.orig_h"] AS s_ip_2;
            flows[j]["id.resp_h"] AS d_ip_2;
            COLLECT SET ((s_ip_1, d_ip_1)) WHERE d_ip_1 == s_ip_2 EXTEND BY (s_ip_2, d_ip_2) AS path_recording;
        WHERE flows[i]["id.resp_p"] == 445; flows[j]["id.resp_p"] == 445
        WRITE output_path/path_recording.json FROM result

In the specifications above:

•	EXTEND BY: The 'extend_by' element is incorporated into the collected set when it fulfills the condition with the existing members. If the collected set is initially empty, the 'extend_by' element becomes the first member.

### Example 9:

REPEAT(LAMBDA) is deprecated.

In this example, the following specifications describe collecting connections as a path linked by RDP connections, where each connection's destination is the next connection's source. Data collection starts with an internet IP address.

In example 9.1, the path length is limited to 5,  the logged source IP along the path is limited to application servers.

In example 9.2,  only the last IP address along the path is logged. 

#### 9.1
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

#### 9.2
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

In conclusion, the KiwiSpec project aims to provide a declarative language and platform for specifying data processing logic for semi-structured data. The key technical aspects of KiwiSpec can be summarized as follows:

1. The language is built on expressions with identifiers in a path to access a semi-structured data value.
2. Data processing is defined through compositional expressions built on top of basic expressions.
3. The output is defined by a template that specifies how to project computed expressions to a user-defined output.
4. The semantics of a specification define a set of values of identifiers instantiated with valid values and expressions calculated with the instantiated identifiers.
5. The final output is generated by populating templates with the calculated expressions.

Overall, KiwiSpec will provide a powerful tool for domain experts to easily specify and maintain their data processing logic, enabling the creation of valuable insights from collected data in various areas such as CYBER ASSET ATTACK SURFACE MANAGEMENT (CAASM), Zero Trust analytics, and threat hunting.
