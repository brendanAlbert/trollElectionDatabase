import sqlite3 as sq
import json
from collections import defaultdict


def connect_to_db():
    """
    Establishes connection and pointer to database.
    :return: Returns a tuple containing the connection and cursor
    """
    conn = sq.connect('trolection.sqlite')
    cur = conn.cursor()
    return conn, cur


def clean_db(cur, tables):
    """
    Drops any tables in the database passed in as strings via 'tables'.
    """
    for table in tables:
        cur.execute("DROP TABLE IF EXISTS ?", (table,))


def create_tables(cur):
    """
    Creates tables for database.
    1) State
    2) Candidate
    3) Result - tracks how many electors and votes each candidate got for each state
    """
    state_table_build_query = """
    CREATE TABLE IF NOT EXISTS State(
        state_id INTEGER PRIMARY KEY NOT NULL,
        name TEXT,
        election_date TEXT,
        primary_or_caucus_date TEXT,
        republican_electors INTEGER,
        democratic_electors INTEGER,
        registered_republicans INTEGER,
        registered_democrats INTEGER
    );
    """
    cur.execute(state_table_build_query)

    candidate_table_build_query = """
    CREATE TABLE IF NOT EXISTS Candidate(
        id INTEGER PRIMARY KEY NOT NULL,
        name TEXT NOT NULL,
        party TEXT NOT NULL,
        total_votes INTEGER,
        delegate_tally INTEGER
    );
    """
    cur.execute(candidate_table_build_query)

    results_table_build_query = """
    CREATE TABLE IF NOT EXISTS Result(
        state_id INTEGER,
        candidate_id INTEGER,
        votes_received INTEGER,
        delegates_awarded INTEGER
    );
    """
    cur.execute(results_table_build_query)


def get_candidate_results_dictionary(cur):
    """
    'SELECT name, california_electors_won FROM Candidate'
    'SELECT name, california_votes_won FROM Candidate'
    'SELECT ? FROM Candidate WHERE name = ? '
    """

    list_of_states = [
        'alabama',
        'alaska',
        'arizona',
        'arkansas',
        'california',
        'colorado',
        'connecticut',
        'delaware',
        'district_of_columbia',
        'florida',
        'georgia',
        'hawaii',
        'idaho',
        'illinois',
        'indiana',
        'iowa',
        'kansas',
        'kentucky',
        'louisiana',
        'maine',
        'maryland',
        'massachusetts',
        'michigan',
        'minnesota',
        'mississippi',
        'missouri',
        'montana',
        'nebraska',
        'nevada',
        'new_hampshire',
        'new_jersey',
        'new_mexico',
        'new_york',
        'north_carolina',
        'north_dakota',
        'ohio',
        'oklahoma',
        'oregon',
        'pennsylvania',
        'rhode_island',
        'south_carolina',
        'south_dakota',
        'tennessee',
        'texas',
        'utah',
        'vermont',
        'virginia',
        'washington',
        'west_virginia',
        'wisconsin',
        'wyoming'
    ]

    list_of_state_electors_fields = [
        'alabama_electors_won',
        'alaska_electors_won',
        'arizona_electors_won',
        'arkansas_electors_won',
        'california_electors_won',
        'colorado_electors_won',
        'connecticut_electors_won',
        'delaware_electors_won',
        'district_of_columbia_electors_won',
        'florida_electors_won',
        'georgia_electors_won',
        'hawaii_electors_won',
        'idaho_electors_won',
        'illinois_electors_won',
        'indiana_electors_won',
        'iowa_electors_won',
        'kansas_electors_won',
        'kentucky_electors_won',
        'louisiana_electors_won',
        'maine_electors_won',
        'maryland_electors_won',
        'massachusetts_electors_won',
        'michigan_electors_won',
        'minnesota_electors_won',
        'mississippi_electors_won',
        'missouri_electors_won',
        'montana_electors_won',
        'nebraska_electors_won',
        'nevada_electors_won',
        'new_hampshire_electors_won',
        'new_jersey_electors_won',
        'new_mexico_electors_won',
        'new_york_electors_won',
        'north_carolina_electors_won',
        'north_dakota_electors_won',
        'ohio_electors_won',
        'oklahoma_electors_won',
        'oregon_electors_won',
        'pennsylvania_electors_won',
        'rhode_island_electors_won',
        'south_carolina_electors_won',
        'south_dakota_electors_won',
        'tennessee_electors_won',
        'texas_electors_won',
        'utah_electors_won',
        'vermont_electors_won',
        'virginia_electors_won',
        'washington_electors_won',
        'west_virginia_electors_won',
        'wisconsin_electors_won',
        'wyoming_electors_won'
    ]
    list_of_state_votes_fields = [
        'alabama_votes_won',
        'alaska_votes_won',
        'arizona_votes_won',
        'arkansas_votes_won',
        'california_votes_won',
        'colorado_votes_won',
        'connecticut_votes_won',
        'delaware_votes_won',
        'district_of_columbia_votes_won',
        'florida_votes_won',
        'georgia_votes_won',
        'hawaii_votes_won',
        'idaho_votes_won',
        'illinois_votes_won',
        'indiana_votes_won',
        'iowa_votes_won',
        'kansas_votes_won',
        'kentucky_votes_won',
        'louisiana_votes_won',
        'maine_votes_won',
        'maryland_votes_won',
        'massachusetts_votes_won',
        'michigan_votes_won',
        'minnesota_votes_won',
        'mississippi_votes_won',
        'missouri_votes_won',
        'montana_votes_won',
        'nebraska_votes_won',
        'nevada_votes_won',
        'new_hampshire_votes_won',
        'new_jersey_votes_won',
        'new_mexico_votes_won',
        'new_york_votes_won',
        'north_carolina_votes_won',
        'north_dakota_votes_won',
        'ohio_votes_won',
        'oklahoma_votes_won',
        'oregon_votes_won',
        'pennsylvania_votes_won',
        'rhode_island_votes_won',
        'south_carolina_votes_won',
        'south_dakota_votes_won',
        'tennessee_votes_won',
        'texas_votes_won',
        'utah_votes_won',
        'vermont_votes_won',
        'virginia_votes_won',
        'washington_votes_won',
        'west_virginia_votes_won',
        'wisconsin_votes_won',
        'wyoming_votes_won'
    ]
    candidates = ['johnson', 'west', 'winfrey']
    candidate_results_dictionary = {}
    candidate_results_dictionary['johnson'] = {}
    candidate_results_dictionary['johnson']['electors'] = {}
    candidate_results_dictionary['west'] = {}
    candidate_results_dictionary['west']['electors'] = {}
    candidate_results_dictionary['winfrey'] = {}
    candidate_results_dictionary['winfrey']['electors'] = {}
    '''
    > d = {}
    > d['johnson'] = {}
    > d['johnson']['electors'] = {}
    > d
    > {'johnson': {'electors': {}}}
    > d['johnson']['electors']['alabama'] = 12
    > d['johnson']['electors']['alaska'] = 10
    > d
    > {'johnson': {'electors': {'alabama': 12, 'alaska': 10}}}
    '''

    query = "SELECT ? FROM Candidate WHERE name = ?"

    for candidate in candidates:
        for idx, state_field in enumerate(list_of_state_electors_fields):  # electors
            cur.execute(query, (state_field, candidate,))
            candidate_results_dictionary[candidate]['electors'][list_of_states[idx]] = cur.fetchone()[0]
        for idx, state_field in enumerate(list_of_state_votes_fields):  # votes
            cur.execute(query, (state_field, candidate,))
            candidate_results_dictionary[candidate]['votes'][list_of_states[idx]] = cur.fetchone()[0]

    return candidate_results_dictionary


def populate_result_table(cur):
    """
    Populates the Result table with data from a json file.
    """
    # query = """
    """
    INSERT INTO Result(
        state_id,
        candidate_id,
        votes_received,
        delegates_awarded
    )
    VALUES(
        ?,?,?,?
    );
    """
    pass
    # cur.execute(query,(,))


def populate_candidate_table(conn, cur):
    """
        Populates the Candidate table with data from a json file.
    """
    query = """
    INSERT INTO Candidate(name,party) VALUES ( ?,? );
    """

    data = {}
    with open('candidates.json') as f:
        data = json.load(f)
    for c in data['candidates']:
        cur.execute(query, (c['name'], c['party']))
    conn.commit()
    print("Candidate table successfully populated!")


def populate_state_table(cur, conn):
    """
        Populates the State table with data from a json file.
    """
    pass
    query = """
    INSERT INTO State(
        name TEXT,
        primary_or_caucus_date TEXT,
        republican_electors INTEGER,
        democratic_electors INTEGER,
        number_registered_republicans INTEGER,
        number_registered_democrats INTEGER
    ) VALUES (
        ?, ?, ?, ?, ?, ?
    );
    """

    date = {}
    with open('states.json') as f:
        data = json.load(f)
    for s in data['states']:
        cur.execute(query, (
        s['state_id'], s['name'], s['election_date'], s['republican_delegates'], s['democratic_delegates'],
        s['registered_republicans'], s['registered_democrats'], s['partial_winnings']))
    conn.commit()
    print("State table successfully populated!")


def get_dict_load_json_from_file():
    data = {}
    with open('candidate_data.json') as f:
        data = json.load(f)  # data is a dictionary
    '''
    data is a dictionary of this form
    {
        'johnson' : {  <-- data['johnson']
            'name': '', <- data['johnson']['name']
            'party': '',
            'electors' : {},
            'votes': {}
        },
        'west' : {
            'name': '',
            'party': '',
            'electors' : {},
            'votes': {}
        },
    }
    '''

    # pretty_data = json.dumps(data, sort_keys=True, indent=4 * ' ')
    # pretty_data = json.loads(data)
    # print(data['johnson']['name'])
    # print(data['johnson']['party'])
    # print(data['johnson']['electors'])

    return data


def main():
    pass
    # tables = ['States', 'Candidates']

    # Connect to db
    # conn, cur = connect_to_db()

    # If we want to clean the database by dropping tables
    # clean_db(cur, tables)

    # tables already made!
    # create_tables(cur)

    # Candidate table already populated!
    # populate_candidate_table(conn, cur)


if __name__ == "__main__":
    main()
