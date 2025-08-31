#!/usr/bin/env python3
"""
Simple migration script to add role column to users table
Run this after starting the database to add the role column
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def migrate():
    # Get database connection details
    db_url = os.getenv("DATABASE_URL", "postgresql://verdictvault:password@localhost:5432/verdictvault")
    
    try:
        # Connect to database
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Check if role column exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'role'
        """)
        
        if cursor.fetchone():
            print("Role column already exists")
        else:
            # Add role column
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN role VARCHAR DEFAULT 'user'
            """)
            
            # Update existing users to have admin role for testing
            cursor.execute("""
                UPDATE users 
                SET role = 'admin' 
                WHERE email = 'test@example.com'
            """)
            
            conn.commit()
            print("Successfully added role column and set test user as admin")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Migration failed: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    migrate()