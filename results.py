import sqlite3 as sq

# make db connection
def connect():
    """
    Connect to the database

    Returns conn, a connection object
    Returns curr, a pointer (cursor) to con
    """
    conn = sq.connect("election_db.sqlite")
    curr = conn.cursor()
    return conn, curr

# clean old tables
def cleandb(curr):
    """
    drop the tables if they exist so they don't make errors

    Param:  curr, a cursor to an existing database connection
            tables, list of table names
    """
    cmd = """
    DROP TABLE IF EXISTS Results;
    DROP TABLE IF EXISTS State;
    DROP TABLE IF EXISTS Candidate;
    """
    curr.executescript(cmd)

# create results table
def make_tables(curr, conn):
    cmd = """
    CREATE TABLE Candidate(
    candidate_id INTEGER PRIMARY KEY NOT NULL,
    name TEXT,
    party TEXT,
    total_votes INTEGER,
    delegate_tally INTEGER,
    age INTEGER,
    sex TEXT,
    phone_number TEXT);

    CREATE TABLE State(
    state_id INTEGER PRIMARY KEY NOT NULL,
    name TEXT,
    election_date TEXT,
    republican_delegates INTEGER,
    democrat_delegates INTEGER,
    registered_republicans INTEGER,
    registered_democrates INTEGER,
    partial_winnings BOOL
    );
    """
    curr.executescript(cmd)
    conn.commit()

#first populate state and candidate
def populate_state_cand(curr, conn):
    cmd = """
    INSERT INTO State(name, election_date, republican_delegates, democrat_delegates, registered_republicans, registered_democrates, partial_winnings)
    VALUES("CA", "19-3-3", 100, 200, 500, 1000, 1),
    ("AZ", "19-3-1", 100, 100, 500, 800, 0),
    ("WA", "19-4-4", 200, 300, 600, 7000, 0);

    INSERT INTO Candidate(name, party, total_votes, delegate_tally, age, sex, phone_number)
    VALUES("Oprah Winfrey", "Democrat", 0, 0, 64, "F", "323-602-5500"),
    ("The Rock", "Democrat", 0, 0, 45, "M", "310-285-9000"),
    ("Kanye West", "Republican", 0, 0, 40, "M", "661-748-0240");
    """
    curr.executescript(cmd)
    conn.commit()

########################### BELOW THIS LINE ARE METHODS EXCLUSIVE TO THIS FILE (UNCOMMENT ABOVE IF YOU WANT THIS TO BE A STANDALONE
########################### FILE)

# specifically make a create_results()
def create_results(curr,conn):
    cmd = """
    CREATE TABLE Results(
    state_id INTEGER,
    candidate_id INTEGER,
    votes_received INTEGER,
    delegates_awarded INTEGER,
    PRIMARY KEY(state_id, candidate_id)
    );
    """
    curr.execute(cmd)

def insert_result(curr, conn, state_name, candidate_name, votes):
    """
    Given the state name, candidate name, and the number of votes that candidate received, this function will create
    a result entry in the database. It will automatically find the state_id and candidate_id from the names in
    the parameters. It will also calculate the number of delegates awarded based on the number of votes, the state's
    registered voters in that candidate's party, and if that state allows partial delegate awards.

    Parameters: curr, a cursor to conn
                conn, a connection object to a database file
                state_name, text name of the state the result is for
                candidate_name, text name of the candidate the result is for
                votes, the integer number of votes the candidate received in this state's primary
    """
    # id = a tuple with state_id, candidate_id
    id = find_ids(curr, state_name, candidate_name)
    # update votes for candidate total
    update_total_votes(curr, id[1], votes)

    cmd = """
    INSERT INTO Results(state_id, candidate_id, votes_received, delegates_awarded)
    VALUES({}, {}, {}, 0);
    """.format(id[0], id[1], votes)
    curr.execute(cmd)

    calc_delegates(curr, id[0], id[1])
    conn.commit()

def find_ids(curr, state_name, candidate_name):
    """
    Takes state and candidate name and returns their respective IDs.

    Param:  curr, a cursor to a database connection object
            state_name, TEXT name of a state
            candidate_name, TEXT name of a candidate

    Return: a tuple containing: s_id, INTEGER ID of a state
                                c_id, INTEGER ID of a candidate
    """
    # # Find the state and candidate id
    cmd = """
    SELECT state_id FROM State
    WHERE name = "{}";
    """.format(state_name)
    curr.execute(cmd)
    s_id = curr.fetchall()[0]

    cmd2 = """
    SELECT candidate_id FROM Candidate
    WHERE name = "{}"
    """.format(candidate_name)
    curr.execute(cmd2)
    c_id = curr.fetchall()[0]
    return s_id[0], c_id[0]

def calc_delegates(curr, state_id, candidate_id):
    """
    This function will first check if all entries for this party in this state have been entered.
    If they haven't, it will return. If they have, it will call update_delegates for the entries in that state.

    Param:  curr, a cursor to a database connection object
            state_id, INTEGER representing the state id of the current state entering primary results
    """
    # what is this candidate's party?
    get_party = """
    SELECT party FROM Candidate
    WHERE Candidate.candidate_id = {}
    """.format(candidate_id)
    curr.execute(get_party)
    party = curr.fetchone()[0]

    # find the number of candidates with the same party affiliation
    cmd = """
    SELECT COUNT(my_party) FROM (SELECT Candidate.candidate_id AS my_party FROM Candidate WHERE Candidate.party = "{}");
    """.format(party)
    curr.execute(cmd)
    party_count = curr.fetchall()[0]

    # find current number of candidates of that party who have entries for that state primary
    get_result_count = """
    SELECT COUNT(this_party) FROM (SELECT Results.candidate_id AS this_party FROM Results
    JOIN Candidate ON Candidate.candidate_id = Results.candidate_id
    WHERE Results.state_id = {} AND Candidate.party = "{}");
    """.format(state_id, party)
    curr.execute(get_result_count)
    current_count = curr.fetchall()

    if (current_count[0] == party_count):
        award(curr, state_id, party)

def award(curr, state_id, party):
    """
    Calculates award after all votes for a state primary have been submitted. Updates results and candidate delegate count.

    Param:  curr, a cursor to a database's connection object
            state_id, the INTEGER of state ID we are concerned with.

    """
    # find amount of delegates that state can award for this party.
    delegates = award_amount(curr, state_id, party)

    # first, figure out if state allows partial awards and how many delegates it awards
    if (check_award(curr, state_id)):
        # partial award IS allowed. find % of delegates to give to each candidate
        # get number of votes each candidate recieved for that state_id. use those percentages * delegates
        cmd = """
        SELECT Results.candidate_id FROM Results
        JOIN Candidate ON Candidate.candidate_id = Results.candidate_id
        WHERE Results.state_id = {} AND Candidate.party = "{}"
        ORDER BY Candidate.candidate_id;
        """.format(state_id, party)
        curr.execute(cmd)
        ids = curr.fetchall()

        cmd2 = """
        SELECT votes_received FROM Results
        JOIN Candidate ON Candidate.candidate_id = Results.candidate_id
        WHERE Results.state_id = {} AND Candidate.party = "{}"
        ORDER BY Candidate.candidate_id
        """.format(state_id, party)
        curr.execute(cmd2)
        votes = curr.fetchall()

        # now lets find the total votes cast in that state for that party:
        vote_sum = 0

        for vote in votes:
            vote_sum += vote[0]


        # and now we make a list of percentages
        delegate_list = []
        for vote in votes:
            delegate_list.append((float(vote[0])/float(vote_sum)) * float(delegates))

        for id, delegate in zip(ids, delegate_list):
            update_delegates(curr, id[0], state_id, delegate)

    else:
        # winner take all. Give all delegates to the candidate with the most votes from that state.
        cmd = """
        SELECT winner, MAX(votes) FROM (
        SELECT candidate_id AS winner, votes_received AS votes FROM Results
        WHERE Results.state_id = {}
        );
        """.format(state_id)
        curr.execute(cmd)
        state_party_winner = curr.fetchall()
        # call a function to change the winner's delegate count in TWO places (candidate table and results table)
        update_delegates(curr, state_party_winner[0], state_id, delegates)

def update_delegates(curr, candidate_id, state_id, delegates):
    """
    Updates delegate count for both the results table and for the candidate total tally.

    Param:  curr, a cursor to a database connection object
            candidate_id, the INTEGER ID of the candidate to update
            state_id, the INTEGER ID of the state to update results for
            delegates, the INTEGER of delegates to award the candidate
    """
    # first retrieve the current delegate count of the candidate from the candidate table
    get_count = """
    SELECT delegate_tally FROM Candidate
    WHERE candidate_id = {}
    """.format(candidate_id)
    curr.execute(get_count)
    current_count = curr.fetchall()[0]
    new_count = current_count[0] + delegates
    new_count = int(round(new_count))
    delegates = int(round(delegates))

    cmd = """
    UPDATE Results
    SET delegates_awarded = {}
    WHERE Results.state_id = {} AND Results.candidate_id = {};
    UPDATE Candidate
    SET delegate_tally = {}
    WHERE candidate_id = {};
    """.format(delegates, state_id, candidate_id, new_count, candidate_id)
    curr.executescript(cmd)

def check_award(curr, state_id):
    """
    Checks if that state awards partial delegates.

    Param:  curr, a cursor to a connection object
            state_id, INTEGER ID of state being checked

    Return: check_delegates, a BOOL for if partial award is allowed (False means it is not)
    """
    cmd = """
    SELECT partial_winnings FROM STATE
    WHERE State.state_id = {}
    """.format(state_id)
    curr.execute(cmd)
    check_delegates = curr.fetchall()[0]

    return check_delegates

def award_amount(curr, state_id, party):
    """
    Finds the number of delegates that state awards for that party's primary

    Param:  curr, a cursor to a database connection object
            state_id, INTEGER ID of state
            party, the party we are awarding delegates to

    Return: delegates, INTEGER of delegates this state rewards
    """
    if party == "Republican":
        cmd = """
        SELECT republican_delegates FROM State
        WHERE State.state_id = {}
        """.format(state_id)
    else:
        # We currently only have candidates affiliates with Republicans or Democrats
        cmd = """
        SELECT democrat_delegates FROM State
        WHERE State.state_id = {}
        """.format(state_id)

    curr.execute(cmd)
    return curr.fetchone()[0]

def update_total_votes(curr, candidate_id, votes):
    """
    Updates the total votes a candidate has in the Candidate table

    Param:  curr, a cursor to a database connection object
            candidate_id, the INTEGER ID of the candidate to update
            votes, the INTEGER number of votes to add to a candidate's vote tally
    """
    # first retreive the existing vote total
    get_votes = """
    SELECT total_votes FROM Candidate
    WHERE candidate_id = {}
    """.format(candidate_id)
    curr.execute(get_votes)
    old_total = curr.fetchone()[0]
    new_total = old_total + votes
    new_total = int(round(new_total))

    cmd = """
    UPDATE Candidate
    SET total_votes = {}
    WHERE candidate_id = {}
    """.format(new_total, candidate_id)
    curr.execute(cmd)

# ################Display FUNCTIONS! #######################
# All competitors alphabetically
def display_all_candidates(curr):
    """
    Returns all candidates in alphabetical order.

    Param: curr, a cursor to a database connection object
    Return: a list of all candidates in lexigraphical order
    """
    cmd = """
    SELECT Candidate.name FROM Candidate
    ORDER BY Candidate.name;
    """
    curr.execute(cmd)
    data = curr.fetchall()
    candidate_list = []

    for entry in data:
        candidate_list.append(entry[0])

    return candidate_list

# Competitors and their bib numbers (or whatever number they have)
def display_candidates_and_ids(curr):
    """
    Returns all candidates and their IDs.

    Param: curr, a cursor to a database connection object
    Return: a list of tuples containing candidate names and ids
    """
    cmd = """
    SELECT Candidate.name, Candidate.candidate_id FROM Candidate
    ORDER BY Candidate.candidate_id;
    """
    curr.execute(cmd)
    data = curr.fetchall()

    return data

# All male competitors
def display_all_male_competitors(curr):
    """
    Returns all male candidates.

    Param: curr, a cursor to a database connection object
    Return: a list of male candidate names
    """
    cmd = """
    SELECT Candidate.name FROM Candidate
    WHERE Candidate.sex = "M"
    ORDER BY Candidate.name;
    """
    curr.execute(cmd)
    data = curr.fetchall()
    candidate_list = []

    for entry in data:
        candidate_list.append(entry[0])

    return candidate_list

# All female competitors
def display_all_female_competitors(curr):
    """
    Returns all female candidates.

    Param: curr, a cursor to a database connection object
    Return: a list of female candidate names
    """
    cmd = """
    SELECT Candidate.name FROM Candidate
    WHERE Candidate.sex = "F"
    ORDER BY Candidate.name;
    """
    curr.execute(cmd)
    data = curr.fetchall()
    candidate_list = []

    for entry in data:
        candidate_list.append(entry[0])

    return candidate_list

# All events, listed by starting time
def display_all_events(curr):
    """
    Returns all primaries listed by event date
    NOTE: The election_dates in the state tables MUST be in the format YY-MM-DD for this to work!

    Param: curr, a cursor to a database connection object
    Return: a list of all state names that will have primaries
    """
    cmd = """
    SELECT State.name FROM State
    ORDER BY State.election_date
    """
    curr.execute(cmd)
    data = curr.fetchall()
    state_list = []

    for entry in data:
        state_list.append(entry[0])

    return state_list

# All of the competitors of each event
def display_candidates_by_party(curr, party):
    """
    Returns all candidates of a specified party.

    Param: curr, a cursor to a database connection object
    Return: a list of candidate names
    """
    cmd = """
    SELECT Candidate.name FROM Candidate
    WHERE Candidate.party = "{}"
    ORDER BY Candidate.name;
    """.format(party)
    curr.execute(cmd)
    data = curr.fetchall()
    candidate_list = []

    for entry in data:
        candidate_list.append(entry[0])

    return candidate_list

# The top winners of each event
def display_top_competitors(curr, state_name):
    """
    Lists all competitors who currently have results for a state primary with the winner or current lead for that state listed first
    NOTE: will return an empty list if there are no results for a primary in that state yet

    Param:  curr, a cursor to a database connection object
            state_name, the TEXT name of a state you want to check

    Return: list of competitor TEXT names
    """
    # get competitor names from a JOINT table of results and candidate
    cmd = """
    SELECT Candidate.name FROM Candidate
    JOIN Results ON Candidate.candidate_id = Results.candidate_id
    JOIN State ON State.state_id =  Results.state_id
    WHERE State.name = "{}"
    ORDER BY Results.votes_received;
    """.format(state_name)
    curr.execute(cmd)
    candidates = curr.fetchall()

    # lets make a list of candidates to return. I don't know how many will be here so i will use a loop to iterate through.
    can_list = []

    for hopeful in candidates:
        can_list.append(hopeful[0])

    return can_list


# You should allow the user to look up (at least)
# A person’s id given their name, event, and age
def look_up_id (curr, name, age):
    """
    Look up a candidate's ID by their name and age

    Param:  curr, a cursor to a database connection object
            name, TEXT name of candidate
            age, INTEGER age of canidate

    Return: candidate's ID
    """
    cmd = """
    SELECT candidate_id FROM Candidate
    WHERE name = "{}" AND age = {}
    """.format(name, age)
    curr.execute(cmd)
    c_id = curr.fetchall()[0]
    return c_id[0]

# A person’s information given their id number
def look_up_info_by_id (curr, id):
    """
    Finds a candidate's information based on their ID number.

    Param:  curr, a cursor to a database connection object
            id, an INTEGER ID of the candidate

    Return: a tuple of the candidate's information in the following order:
            candidate_id, name, party, total_votes, delegate_tally, age, sex, phone_number
    """
    cmd = """
    SELECT * FROM Candidate
    WHERE Candidate.candidate_id = {}
    """.format(id)
    curr.execute(cmd)
    return curr.fetchall()[0]

# A person’s overall time (or whatever you’re tracking to determine winners)
# given their name or id (if matching by name, it’s OK if multiple people are returned)
def look_up_total_votes_by_name(curr, name):
    """
    Look up a candidate's total votes won using their name.

    Param:  curr, a cursor to a database connection object
            name, TEXT name of the candidate

    Return: INTEGER number of votes the candiate has won so far
    """
    cmd = """
    SELECT Candidate.total_votes FROM Candidate
    WHERE Candidate.name = "{}";
    """.format(name)
    curr.execute(cmd)
    return curr.fetchall()[0][0]

def look_up_total_votes_by_id (curr, id):
    """
    Look up a candidate's total votes won using their ID number.

    Param:  curr, a cursor to a database connection object
            id, INTEGER ID of the candidate

    Return: INTEGER number of votes the candiate has won so far
    """
    cmd = """
    SELECT Candidate.total_votes FROM Candidate
    WHERE Candidate.candidate_id = "{}";
    """.format(id)
    curr.execute(cmd)
    return curr.fetchall()[0][0]

# A person’s award(s) given their id number
def look_up_delegate_tally (curr, id):
    """
    Look up a candidate's total delegates using their ID number.

    Param:  curr, a cursor to a database connection object
            id, INTEGER ID of the candidate

    Return: INTEGER number of delegates the candiate has won so far
    """
    cmd = """
    SELECT Candidate.delegate_tally FROM Candidate
    WHERE Candidate.candidate_id = "{}";
    """.format(id)
    curr.execute(cmd)
    return curr.fetchall()[0][0]

# make method to delete data

# make method to edit data

def main():
    conn, curr = connect()
    cleandb(curr)
    make_tables(curr, conn)
    create_results(curr, conn)
    populate_state_cand(curr, conn)
    insert_result(curr, conn, "CA", "Oprah Winfrey", 1000)
    insert_result(curr, conn, "CA", "The Rock", 500)
    insert_result(curr, conn, "WA", "Oprah Winfrey", 800)
    insert_result(curr, conn, "CA", "Kanye West", 500)
    print(display_all_candidates(curr))
    print(display_candidates_and_ids(curr))
    print(display_all_male_competitors(curr))
    print(display_all_female_competitors(curr))
    print(display_candidates_by_party(curr, "Democrat"))
    print(display_candidates_by_party(curr, "Republican"))
    print(display_all_events(curr))
    print(display_top_competitors(curr, "CA"))
    print(display_top_competitors(curr, "VE")) # empty list (no data)
    print(look_up_id (curr, "Oprah Winfrey", 64))
    print(look_up_info_by_id (curr, 1))
    print(look_up_total_votes_by_name(curr, "Oprah Winfrey"))
    print(look_up_total_votes_by_id (curr, 1))
    print(look_up_delegate_tally (curr, 1))

if __name__ == "__main__":
    main()
