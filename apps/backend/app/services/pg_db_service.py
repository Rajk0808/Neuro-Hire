from fastapi import Request

async def execute_query(query, params=None):
    connection = Request.state.pg_connection if hasattr(Request.state, 'pg_connection') else None
    if connection is None:
        return None
    
    query_params = params if params is not None else ()
    if not isinstance(query_params, (list, tuple)):
        query_params = (query_params,)

    try:
        # Check if it is a read query (SELECT)
        if query.strip().lower().startswith("select"):
            # asyncpg uses .fetch() to grab all rows directly. No cursor needed!
            result = await connection.fetch(query, *query_params)
            return result
        else:
            # For INSERT/UPDATE/DELETE, wrap it in an atomic transaction.
            # This replaces manual connection.commit()
            async with connection.transaction():
                await connection.execute(query, *query_params)
            return True
            
    except Exception as e:
        print(f"Error executing query: {e}")
        return None
        
    finally:
        # Crucial: Always close raw connections to prevent pool exhaustion
        await connection.close()

async def create_db():
    try:
        await execute_query("""
CREATE TYPE seniority_level AS ENUM ( 'junior', 'mid', 'senior', 'staff', 'principal' ); 
CREATE TYPE job_status AS ENUM ( 'draft', 'open', 'screening', 'interviewing', 'closed' ); 
CREATE TYPE candidate_status AS ENUM ( 'applied', 'screened', 'shortlisted', 'rejected', 'hired', 'interview_scheduled', 'interview_completed', 'interviewing', 'offer_sent' ); 
CREATE TYPE agent_state AS ENUM ( 'idle', 'running', 'completed', 'failed', 'paused' ); 

-- USERS
CREATE TABLE IF NOT EXISTS users ( 
    id SERIAL PRIMARY KEY, 
    name VARCHAR(255) NOT NULL, 
    email VARCHAR(255) UNIQUE NOT NULL, 
    password VARCHAR(255) NOT NULL, 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
); 

-- JOBS
CREATE TABLE IF NOT EXISTS jobs ( 
    id SERIAL PRIMARY KEY, 
    title VARCHAR(255) NOT NULL, 
    description TEXT NOT NULL, 
    department VARCHAR(255) NOT NULL, 
    location VARCHAR(255) NOT NULL, 
    seniority seniority_level NOT NULL, 
    status job_status NOT NULL DEFAULT 'draft', 
    salary_min INTEGER NOT NULL, 
    salary_max INTEGER NOT NULL, 
    currency VARCHAR(10) NOT NULL, 
    required_skills TEXT[] NOT NULL, 
    nice_to_have_skills TEXT[] DEFAULT '{}', 
    dei_score INTEGER NOT NULL CHECK (dei_score BETWEEN 0 AND 100), 
    applications_count INTEGER DEFAULT 0, 
    shortlisted_count INTEGER DEFAULT 0, 
    posted_url VARCHAR(500), 
    hiring_manager_id INTEGER NOT NULL, 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
    CONSTRAINT salary_check CHECK (salary_min <= salary_max), 
    CONSTRAINT fk_hiring_manager FOREIGN KEY (hiring_manager_id) REFERENCES users(id) ON DELETE CASCADE 
); 

-- CANDIDATES
CREATE TABLE IF NOT EXISTS candidates ( 
    id UUID PRIMARY KEY, 
    name VARCHAR(255) NOT NULL, 
    email VARCHAR(255) UNIQUE NOT NULL, 
    location VARCHAR(255), 
    current_company VARCHAR(255), 
    current_role VARCHAR(255), 
    experience_years INTEGER DEFAULT 0, 
    skills TEXT[] DEFAULT '{}', 
    status candidate_status DEFAULT 'applied', 
    bm25_score DECIMAL(10,4) DEFAULT 0, 
    vector_score DECIMAL(10,4) DEFAULT 0, 
    graph_score DECIMAL(10,4) DEFAULT 0, 
    rrf_score DECIMAL(10,4) DEFAULT 0, 
    bias_flag BOOLEAN DEFAULT FALSE, 
    resume_url TEXT NOT NULL, 
    linkedin_url TEXT, 
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
); 

-- JOB APPLICATIONS
CREATE TABLE IF NOT EXISTS job_applications ( 
    id SERIAL PRIMARY KEY, 
    job_id INTEGER NOT NULL, 
    candidate_id UUID NOT NULL, 
    status candidate_status DEFAULT 'applied', 
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
    UNIQUE(job_id, candidate_id), 
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE, 
    FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE 
); 

-- AGENTS
CREATE TABLE IF NOT EXISTS agents ( 
    id UUID PRIMARY KEY, 
    agent VARCHAR(255) NOT NULL, 
    state agent_state NOT NULL DEFAULT 'idle', 
    message TEXT, 
    progress INTEGER DEFAULT 0 CHECK (progress BETWEEN 0 AND 100), 
    application_id INTEGER, 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
    FOREIGN KEY (application_id) REFERENCES job_applications(id) ON DELETE CASCADE 
); 

-- SESSIONS
CREATE TABLE IF NOT EXISTS sessions ( 
    id UUID PRIMARY KEY, 
    status VARCHAR(255) NOT NULL, 
    current_draft VARCHAR(255),
    raw_draft TEXT,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE 
); 

-- INDEXES
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status); 
CREATE INDEX IF NOT EXISTS idx_jobs_department ON jobs(department); 
CREATE INDEX IF NOT EXISTS idx_jobs_location ON jobs(location); 
CREATE INDEX IF NOT EXISTS idx_jobs_hiring_manager ON jobs(hiring_manager_id); 
CREATE INDEX IF NOT EXISTS idx_candidates_email ON candidates(email); 
CREATE INDEX IF NOT EXISTS idx_candidates_status ON candidates(status); 
CREATE INDEX IF NOT EXISTS idx_job_applications_job ON job_applications(job_id); 
CREATE INDEX IF NOT EXISTS idx_job_applications_candidate ON job_applications(candidate_id); 
CREATE INDEX IF NOT EXISTS idx_agents_application ON agents(application_id);

        """)
        return True
    except Exception as e:
        print(f"Error creating database: {e}")
        return None
