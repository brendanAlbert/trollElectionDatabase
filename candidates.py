#candidates.py

import sqlite3 as sq
import json
from candidate_class import Candidate
import csv

# 1. Bring in data from json file

# Open the json file 

json_file=open("candidates_info.json")

# Load the json data

candidates=json.load(json_file)

# After loading the json data, close the file.

json_file.close()

# Print the candidates

print("Candidates from the json file:")

# candidates is a dictionary with key value pairs?

print(candidates)

# {'candidates': [{'name': 'Dwayne "The Rock" Johnson',
#                  'delegate_tally': 0,
#                  'age': 45,
#                  'party': 'Republican',
#                  'phone_number': '310-285-9000',
#                  'sex': 'M',
#                  'total_votes': 0},
#                 {'name': 'Oprah Winfrey',
#                  'delegate_tally': 0,
#                  'age': 64,
#                  'party': 'Democrat',
#                  'phone_number': '323-602-5500',
#                  'sex':
#                  'F',
#                  'total_votes': 0},
#                 {'name': 'Kanye West',
#                  'delegate_tally': 0,
#                  'age': 40,
#                  'party': 'Democrat',
#                  'phone_number': '661-748-0240',
#                  'sex': 'M',
#                  'total_votes': 0}]}


# 2. Bring in data from a csv file

path='candidates.csv'
candidates_file=open(path)
print('Candidate data from candidates.csv')
for line in candidates_file:
    print(line)

# name,party,total_votes,delegate_tally,age,sex,phone_number
#
# Dwane “The Rock” Johnson,Republican,0,0,45,M,310-285-9000
#
# Oprah Winfrey,Democrat,0,0,64,F,323-602-5500
#
# Kanye West,Democrat,0,0,40,M,661-748-0240


candidates_file=open(path, newline='')
candidates_reader=csv.reader(candidates_file)
candidates_header=next(candidates_reader)
candidates_values=[row for row in candidates_reader]

print('line by line candidates header and values')
print(candidates_header)
print(candidates_values[0])
print(candidates_values[1])
print(candidates_values[2])

# ['name', 'party', 'total_votes', 'delegate_tally', 'age', 'sex', 'phone_number']
# ['Dwane “The Rock” Johnson', 'Republican', '0', '0', '45', 'M', '310-285-9000']
# ['Oprah Winfrey', 'Democrat', '0', '0', '64', 'F', '323-602-5500']
# ['Kanye West', 'Democrat', '0', '0', '40', 'M', '661-748-0240']

# 3. Parse the csv data

#print("candidates reader:", candidates_reader[0])

# Need to run these 3 lines again?

candidates_file=open(path, newline='')
candidates_reader=csv.reader(candidates_file)
candidates_header=next(candidates_reader)


candidates_data=[]
for row in candidates_reader:
    candidate_name=row[0]
    party=row[1]
    total_votes=int(row[2])
    delegate_tally=int(row[3])
    age=int(row[4])
    sex=row[5]
    phone_number=row[6]
    candidates_data.append([candidate_name, party, total_votes, delegate_tally, age, sex, phone_number])

print("candidates data: ",candidates_data)

# candidates data:  ['Dwane “The Rock” Johnson', 'Republican', 0, 0, 45, 'M', '310-285-9000'],
#                    ['Oprah Winfrey', 'Democrat', 0, 0, 64, 'F', '323-602-5500'],
#                    ['Kanye West', 'Democrat', 0, 0, 40, 'M', '661-748-0240']]

print("########################################################")

# 4. Define functions to enter the data by user input.

conn=sq.connect(':memory:')
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

# Populate candidates table, use context manager

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

cndt_1=Candidate(1,'Oprah Winfrey','Democrat',0 ,0 ,64,'F','323-602-5500')
cndt_2=Candidate(2,'Dwayne "The Rock" Johnson','Republican',0 ,0 ,45 ,'M' ,'310-285-9000')
cndt_3=Candidate(3,'Kanye West','Democrat',0 ,0 ,40 ,'M' ,'661-748-0240')

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
