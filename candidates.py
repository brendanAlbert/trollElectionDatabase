#candidates.py
"""Get candidates from candidates.csv and create 
   candidates.sql dataset.
"""
import csv
import sqlite3

# 1. Get data from csv file and remove column headers

csv_file=open('candidates.csv')
csv_reader=csv.reader(csv_file)
csv_dict_headers=csv.DictReader(csv_file).fieldnames

# 2. Create connection and cursor and conect to and create the database.

conn=sqlite3.connect('election2020.db')
curr=conn.cursor()
conn.commit()

# 3. Create empty table with variable names
#    for the candidates.

curr.execute("""
  create table if not exists candidates(
    candidate_name text,
    party text,
    total_votes integer,
    delegate_tally integer,
    age integer,
    sex text,
    phone_number text
    );""")

# 4. Add values to dataset.  Values originate from the csv file.

curr.executemany("""
    insert into candidates values (?,?,?,?,?,?,?)
    """,
    csv_reader)

# optional: Print the sql data

for row in curr.execute("""
    select * from candidates
    """):
    print(row)

#curr.executemany('INSERT INTO candidates VALUES (?,?,?,?,?,?,?)', csv_reader)
conn.commit()
conn.close()
