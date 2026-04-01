from sqlmodel import create_engine, text

engine = create_engine('postgresql://postgres:postgres@localhost:5432/auto_affiliate')

with engine.connect() as conn:
    try:
        conn.execute(text('ALTER TABLE device ADD COLUMN missed_pings INTEGER DEFAULT 0'))
        print("Added missed_pings")
    except Exception as e:
        print("missed_pings already exists or error:", e)
        
    try:
        conn.execute(text('ALTER TABLE device ADD COLUMN is_active BOOLEAN DEFAULT TRUE'))
        print("Added is_active")
    except Exception as e:
        print("is_active already exists or error:", e)
    
    conn.commit()
