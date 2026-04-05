 -- 1. Add new columns                                                                                                                                                                                                              
ALTER TABLE notes ADD COLUMN id TEXT;                                                                                                                                                                                              
ALTER TABLE notes ADD COLUMN title TEXT NOT NULL DEFAULT 'Untitled';
ALTER TABLE notes ADD COLUMN updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();                                                                                                                                                        
                                                            
-- 2. Give existing rows a UUID                                                                                                                                                                                                    
UPDATE notes SET id = gen_random_uuid()::text WHERE id IS NULL;
                                                                                                                                                                                                                                    
-- 3. Make id NOT NULL
ALTER TABLE notes ALTER COLUMN id SET NOT NULL;                                                                                                                                                                                    
                                                          
-- 4. Drop old primary key (check your constraint name first)                                                                                                                                                                      
-- Run this to find it:
--   SELECT constraint_name FROM information_schema.table_constraints                                                                                                                                                              
--   WHERE table_name = 'notes' AND constraint_type = 'PRIMARY KEY';
ALTER TABLE notes DROP CONSTRAINT notes_pkey;  -- adjust name if different                                                                                                                                                         
                                                                                                                                                                                                                                    
-- 5. Drop old unique constraint on user_id                                                                                                                                                                                        
-- Run this to find it:                                                                                                                                                                                                            
--   SELECT constraint_name FROM information_schema.table_constraints
--   WHERE table_name = 'notes' AND constraint_type = 'UNIQUE';
ALTER TABLE notes DROP CONSTRAINT notes_user_id_key;  -- adjust name if different
                                                                                                                                                                                                                                    
-- 6. Add new constraints
ALTER TABLE notes ADD CONSTRAINT notes_pkey PRIMARY KEY (id);                                                                                                                                                                      
ALTER TABLE notes ADD CONSTRAINT notes_user_title_unique UNIQUE (user_id, title);