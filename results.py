import sqlite3 as sq

# # make db connection
# def connect():
#     """
#     Connect to the database

#     Returns conn, a connection object
#     Returns curr, a pointer (cursor) to con
#     """
#     conn = sq.connect("election_db.sqlite")
#     curr = conn.cursor()
#     return conn, curr

# # clean old tables
# def cleandb(curr):
#     """
#     drop the tables if they exist so they don't make errors

#     Param:  curr, a cursor to an existing database connection
#             tables, list of table names
#     """
#     cmd = """
#     DROP TABLE IF EXISTS Results;
#     DROP TABLE IF EXISTS State;
#     DROP TABLE IF EXISTS Candidate;
#     """
#     curr.executescript(cmd)

# # create results table
# def make_tables(curr, conn):
#     cmd = """
#     CREATE TABLE Candidate(
#     candidate_id INTEGER PRIMARY KEY NOT NULL,
#     name TEXT,
#     party TEXT,
#     total_votes INTEGER,
#     delegate_tally INTEGER);

#     CREATE TABLE State(
#     state_id INTEGER PRIMARY KEY NOT NULL,
#     name TEXT,
#     election_date TEXT,
#     republican_delegates INTEGER,
#     democrat_delegates INTEGER,
#     registered_republicans INTEGER,
#     registered_democrates INTEGER,
#     partial_winnings BOOL
#     );
#     """
#     curr.executescript(cmd)
#     conn.commit()

# #first populate state and candidate
# def populate_state_cand(curr, conn):
#     cmd = """
#     INSERT INTO State(name, election_date, republican_delegates, democrat_delegates, registered_republicans, registered_democrates, partial_winnings)
#     VALUES("CA", "18-3-3", 100, 200, 500, 1000, 1),
#     ("WA", "18-4-4", 200, 300, 600, 7000, 0);

#     INSERT INTO Candidate(name, party, total_votes, delegate_tally)
#     VALUES("Oprah Winfrey", "Democrat", 0, 0),
#     ("The Rock", "Democrat", 0, 0),
#     ("Kanye West", "Republican", 0, 0);
#     """
#     curr.executescript(cmd)
#     conn.commit()

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
    id = find_id(curr, state_name, candidate_name)
    # update votes for candidate total
    update_total_votes(curr, id[1], votes)

    cmd = """
    INSERT INTO Results(state_id, candidate_id, votes_received, delegates_awarded)
    VALUES({}, {}, {}, 0);
    """.format(id[0], id[1], votes)
    curr.execute(cmd)

    calc_delegates(curr, id[0], id[1])
    conn.commit()

def find_id(curr, state_name, candidate_name):
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
    get_id = """
    SELECT party FROM Candidate
    WHERE Candidate.candidate_id = {}
    """.format(candidate_id)
    curr.execute(get_id)
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

# make method to delete data
# still to do!

# def main():
#     conn, curr = connect()
#     cleandb(curr)
#     make_tables(curr, conn)
#     create_results(curr, conn)
#     populate_state_cand(curr, conn)
#     insert_result(curr, conn, "CA", "Oprah Winfrey", 1000)
#     insert_result(curr, conn, "CA", "The Rock", 500)
#     insert_result(curr, conn, "WA", "Oprah Winfrey", 800)
#     insert_result(curr, conn, "CA", "Kanye West", 500)

# if __name__ == "__main__":
#     main()
