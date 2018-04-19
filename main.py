"""
Lab 2Group 1
Brendan Albert
Andria Gazda
Joe Brown
Vincenet Wetzel
"""
import results      # Andria's
import candidates   # Joe's
import states       # Vincent's
import sqlite3
from random import randint





def main():
    conn, cur = results.connect()
    results.cleandb(cur)
    results.make_tables(cur, conn)
    results.create_results(cur, conn)

    # Populate the Candidate table
    candidates.populate_candidate_table(cur, conn)

    # Populate the State table
    states.populate_states_table(cur, conn)

    cur.execute("""
    SELECT name FROM State
    ORDER BY election_date
    LIMIT 25;
    """)
    states_list = cur.fetchall()

    cur.execute("SELECT name from Candidate")
    #print(cur.fetchall()[0][0])
    #cur.execute("SELECT candidate_id from Candidate WHERE name = '{}'".format(cur.fetchall()[0][0]))
    #print(cur.fetchall())
    candidates_list = cur.fetchall()
    #print(candidates_list)

    # Populate Results table
    for hopeful in candidates_list:
        for state in states_list:
            results.insert_result(cur, conn, state[0], hopeful[0], randint(20,300))

    choice = ""
    """
    while (choice != 7):
        print("-------------------------")
        print("Please select an option:")
        # insert_result(curr, conn, "CA", "Kanye West", 500)
        print("1. Add new result")
        # delete_result_row (curr, conn, "CA", "Oprah Winfrey")
        print("2. Delete old result")
        # print(display_all_candidates(curr))

        # print(display_candidates_and_ids(curr))
        # print(display_all_male_competitors(curr))
        # print(display_all_female_competitors(curr))
        # print(display_candidates_by_party(curr, "Democrat"))
        # print(display_candidates_by_party(curr, "Republican"))
        print("3. Display candidates by format")
        # print(display_all_events(curr))
        print("4. Display all events")
        # print(display_top_competitors(curr, "CA"))
        # print(display_top_competitors(curr, "VE")) # empty list (no data)
        print("5. Display top competitors by state")
        # print(look_up_id (curr, "Oprah Winfrey", 64))
        # print(look_up_info_by_id (curr, 1))
        # print(look_up_total_votes_by_name(curr, "Oprah Winfrey"))
        # print(look_up_total_votes_by_id (curr, 1))
        # print(look_up_delegate_tally (curr, 1))
        print("6. Search")
        print("7. I'm done!")

        choice = int(input())
    """



    conn.close()

if __name__ == "__main__":
    main()
