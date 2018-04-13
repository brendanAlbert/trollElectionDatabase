#candidates.py

import sqlite3 as sql
from candidate_class import Candidate

#conn=sql.connect('candidate.db')
conn=sql.connect(':memory:')
curr=conn.cursor()

# Create empty candidates table

curr.execute(
    """CREATE TABLE candidates(
    candidate_id   INT PRINARY KEY NOT NULL,
    candidate_name text,
    party          text,
    total_votes    int,
    delegate_tally int,
    age            int,
    sex            text,
    phone_number   text);"""
)

# Populate candidates table

def insert_candidate(cndt):
    with conn:
        curr.execute("""INSERT INTO candidates 
                        VALUES(:candidate_id,
                               :candidate_name,
                               :party,
                               :total_votes,
                               :delegate_tally,
                               :age,
                               :sex,
                               :phone_number);""",
                    {'candidate_id':   cndt.candidate_id,
                     'candidate_name': cndt.candidate_name,
                     'party':          cndt.party,
                     'total_votes':    cndt.total_votes,
                     'delegate_tally': cndt.delegate_tally,
                     'age':            cndt.age,
                     'sex':            cndt.sex,
                     'phone_number':   cndt.phone_number})

# Select a particular candidate by name

def get_candidates_by_name(name):
    curr.execute("SELECT * FROM candidates WHERE candidate_name=:candidate_name;",
                 {'candidate_name': name})
    return curr.fetchall()

# Update total votes and delegate tally.

def update_party(cndt, party):
    with conn:
        curr.execute("""UPDATE candidates SET party = :party
                        WHERE candidate_name = :candidate_name;""",
                     {'candidate_name': cndt.candidate_name, 'party': party})

def update_total_votes(cndt, total_votes):
    with conn:
        curr.execute("""UPDATE candidates SET total_votes = :total_votes
                        WHERE candidate_name = :candidate_name;""",
                     {'candidate_name': cndt.candidate_name, 'total_votes': total_votes})

def update_delegates(cndt, delegate_tally):
    with conn:
        curr.execute("""UPDATE candidates SET delegate_tally = :delegate_tally
                        WHERE candidate_name = :candidate_name;""",
                     {'candidate_name': cndt.candidate_name, 'delegate_tally': delegate_tally})


# Remove a candidate

def remove_candidate(cndt):
     with conn:
         curr.execute("DELETE FROM candidates WHERE candidate_name=:candidate_name",
                      {'candidate_name': cndt.candidate_name})


curr.execute("""INSERT INTO candidates VALUES
              (4,'Will Smith','Democrat',9000,100,49,'M',' '),
              (5,'Chris Rock','Democrat',9000,100,53,'M',' ');
                """)


# Create candidate records

cndt_1=Candidate(1,'Oprah Winfrey','Democrat',9500,100,64,'F','(323)602-5500')
cndt_2=Candidate(2,'Dwayne "The Rock" Johnson','Republican',9000,100,45,'M','(310)285-9000')
cndt_3=Candidate(3,'Kanye West','Democrat',8000,100,40,'M',' ')

conn.commit()


insert_candidate(cndt_1)
insert_candidate(cndt_2)
insert_candidate(cndt_3)


cndts=get_candidates_by_name('Dwayne "The Rock" Johnson')
print(cndts)

update_party(cndt_2,"Democrat")
conn.commit()

update_delegates(cndt_3,200)
update_total_votes(cndt_3,15000)
conn.commit()

cndts=get_candidates_by_name('Dwayne "The Rock" Johnson')
print(cndts)


curr.execute("SELECT * FROM candidates")
#
#
# # Methods to iterate through the query result:
#
print(curr.fetchall())

remove_candidate(cndt_1)

curr.execute("SELECT * FROM candidates")

print(curr.fetchall())
#
# #curr.fetchone()    # get one row
# #curr.fetchmany(4)  # return 4 rows as a list
# #curr.fetchall()    # gets all rows
#
# conn.commit()
#
# conn.close()
