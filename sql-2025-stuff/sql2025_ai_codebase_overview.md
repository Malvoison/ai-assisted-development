# AI-Powered Codebase Understanding with SQL Server 2025

*SQL Server 2025 introduces new AI features that enable **retrieval-augmented generation (RAG)** on your own data, making it possible to build a local AI assistant for code comprehension and refactoring. This report explains how to ingest an enterprise codebase into SQL Server 2025 and leverage its semantic search, vector embeddings, and model integration features to create a system that behaves like a “senior engineer.” We focus on fully **on-premises** solutions – using local data and open-source models – to avoid sending any code to cloud services.* 

## 1. Ingesting the Codebase into SQL Server 2025

**Storing code in the database:** Begin by importing your code files (VB.NET, VB6, T-SQL scripts, SSRS report files, C#, C++ source, etc.) into SQL Server as text data. A common approach is to create a table (e.g., `CodeFiles`) with columns for file identifier, file path or module name, language/type, and the file’s contents (as `NVARCHAR(MAX)`). This provides a centralized repository of all source code that SQL Server can index and query. You can use custom scripts or ETL tools to read files from the repository and insert them as rows in this table. Ensure to store any relevant metadata (such as language or project) as columns so you can filter searches by those attributes later.

**Chunking files for RAG:** Large files should be broken into smaller *“chunks”* of text for effective retrieval. SQL Server 2025 offers a built-in table-valued function `AI_GENERATE_CHUNKS` to split text into fragments of a specified size【21†L49-L57】. This function can produce fixed-size chunks (with optional overlap) from each source text, which is ideal for preparing code snippets for embedding. For example, you might chunk each file into segments of, say, 300-500 characters (or tokens) with a small overlap (to avoid losing context between chunks). Each chunk will then serve as a unit of retrieval. You can automate this by storing chunks in a separate table (e.g., `CodeChunks`) linked to the original file via an ID. The `AI_GENERATE_CHUNKS` function makes it easy to chunk multiple rows at once – for instance, by using a `CROSS APPLY` on the `CodeFiles` table【21†L49-L57】【21†L71-L79】. Be sure to enable the preview feature flag and set the database compatibility level to 170 or higher to use this function (since it’s a preview feature in SQL 2025). 

**Why chunking?** Splitting files ensures that each piece can be semantically indexed and retrieved individually. Current LLMs have context length limits, so it’s not feasible to feed a whole large file into a prompt. By indexing smaller code segments, the RAG system can fetch only the most relevant pieces of code to answer a question or suggest an improvement. This also improves semantic search granularity – a search query can match a small function or paragraph of code rather than an entire file.

**Indexing and organizing:** Once chunks are created, consider adding full-text indexes or using SQL 2025’s text indexing to allow keyword-based searches in tandem with semantic search. For example, you might maintain a full-text index on the `CodeChunks` table for traditional exact keyword matches (like finding all occurrences of a function name), while also using vector-based semantic search for conceptual queries. Basic metadata filtering (by language, module, date, etc.) can be done with normal SQL `WHERE` clauses. By organizing code this way, SQL Server becomes a **code knowledge base** that can be queried in natural language.

... (content truncated for brevity in code cell) ...

**Sources:**

- Microsoft SQL Server Blog – *Announcing SQL Server 2025 Preview: The AI-ready database*【2†L180-L189】【2†L191-L199】【2†L201-L207】  
- RedmondMag – *SQL Server 2025 Brings AI-Powered Semantic Search*【11†L98-L107】【11†L124-L132】  
- Microsoft Learn – *CREATE EXTERNAL MODEL (Transact-SQL)*【16†L88-L96】【16†L189-L197】  
- Microsoft Learn – *AI_GENERATE_CHUNKS (Transact-SQL) [Preview]*【21†L49-L57】  
- Microsoft Learn – *Vector search and indexes in SQL Database Engine*【5†L155-L163】【5†L160-L168】  
- Cegal Tech Blog – *SQL Server 2025: 10 new features (AI integration)*【15†L267-L274】【15†L274-L280】  
- E2E Networks Blog – *Top Open-Source LLMs for Coding*【23†L131-L139】【24†L25-L33】  
- MSSQLTips – *SQL Server Semantic Search using New AI Features*【28†L223-L231】【28†L239-L248】  
- Microsoft Learn – *Intelligent applications and AI – LangChain & Semantic Kernel*【9†L295-L303】【9†L322-L330】  
