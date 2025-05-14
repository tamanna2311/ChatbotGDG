-- File Name: schema.sql
-- Purpose: Defines the relational database structure for storing Codeforces problems.
-- Why it exists: A relational DB like SQLite is simple, requires no separate server, 
-- and easily supports structured data filtering (e.g., getting all problems with difficulty < 1500).
-- Used by: db/init_db.py to create the initial tables.
-- Role in pipeline: It forms the foundation of the storage layer. All scraped data ends up here.

CREATE TABLE IF NOT EXISTS problems (
    -- 'id' is a unique auto-incrementing integer for the database's internal use.
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- 'contest_id' and 'problem_index' uniquely identify a problem on Codeforces.
    -- e.g., contest 1500, index A -> problem 1500A.
    contest_id INTEGER NOT NULL,
    problem_index TEXT NOT NULL,
    
    -- 'name' is the human-readable title of the problem.
    name TEXT NOT NULL,
    
    -- 'difficulty' is the Codeforces rating (e.g., 800, 1200, 2000). 
    -- It can be NULL because some problems do not have an assigned rating.
    difficulty INTEGER,
    
    -- 'url' is the direct link to the problem page for easy access.
    url TEXT UNIQUE NOT NULL,
    
    -- 'statement_summary' contains the raw or lightly processed text of the problem.
    -- We store a summary or full text so our RAG pipeline has context to build hints from.
    statement_summary TEXT,
    
    -- We enforce that a combination of contest_id and problem_index is unique.
    UNIQUE(contest_id, problem_index)
);

CREATE TABLE IF NOT EXISTS tags (
    -- A simple table to hold unique problem topics (e.g., "dp", "greedy", "graphs").
    -- Storing them separately normalizes the database.
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS problem_tags (
    -- This is a "junction table" (or "many-to-many table").
    -- Since one problem can have many tags, and one tag can belong to many problems,
    -- this table connects a problem's ID to a tag's ID.
    problem_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    
    -- Establish foreign key relationships to ensure data integrity.
    FOREIGN KEY(problem_id) REFERENCES problems(id),
    FOREIGN KEY(tag_id) REFERENCES tags(id),
    PRIMARY KEY(problem_id, tag_id)
);
