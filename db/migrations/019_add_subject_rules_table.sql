CREATE TABLE subject_rules (
    id SERIAL PRIMARY KEY,
    subject_id INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    rule_label VARCHAR NOT NULL,
    sql_pattern VARCHAR NOT NULL,
    max_count INTEGER DEFAULT 1,
    weight_each FLOAT DEFAULT 0.0,
    CONSTRAINT fk_subject_rules_subject 
        FOREIGN KEY (subject_id) 
        REFERENCES subjects(id) 
        ON DELETE CASCADE
);
