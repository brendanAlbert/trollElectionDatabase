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

    print("Creating database...")

    # Populate the Candidate table
    candidates.populate_candidate_table(cur, conn)

    # Populate the State table
    states.populate_states_table(cur, conn)

    cur.execute("""
    SELECT name FROM State
    ORDER BY election_date ASC
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


    print("Half of the election results are in!")
    choice = ""

    while (choice != 7):
        print("-------------------------")
        print("Please select an option:")
        print("1. Add new result")
        print("2. Delete old result")
        print("3. Display candidates by format")
        print("4. Display all events")
        print("5. Display top competitors by state")
        print("6. Search")
        print("7. I'm done!")

        choice = int(input())
        if choice == 7:
            continue

        elif choice == 1:
            state = input("For which state? ")
            cand = input("For which candidate? ")
            votes = int(input("How many votes? "))
            results.insert_result(cur, conn, state, cand, votes)

        elif choice == 2:
            state = input("For which state? ")
            cand = input("For which candidate? ")
            results.delete_result_row (cur, conn, state, cand)

        elif choice == 3:
            next = ""
            while next != 6:
                print("------------")
                print("Select what number you would like to display:")
                print("1. All candidates alphabetically")
                print("2. All Candidates and their IDs")
                print("3. All male competitors")
                print("4. All female competitors")
                print("5. All candidates by party")
                print("6. Nevermind!")

                next = int(input())

                if next == 6:
                    continue
                elif next == 1:
                    print(results.display_all_candidates(cur))
                elif next == 2:
                    print(results.display_candidates_and_ids(cur))
                elif next == 3:
                    print(results.display_all_male_competitors(cur))
                elif next == 4:
                    print(results.display_all_female_competitors(cur))
                elif next == 5:
                    party = input("Display which party? ")
                    print(results.display_candidates_by_party(cur, party))

        elif choice == 4:
            print(results.display_all_events(cur))

        elif choice == 5:
            state = input("Display top competitors for which state?")
            print(results.display_top_competitors(cur, state))

        elif choice == 6:
            my_choice = ""
            while my_choice != 6:
                print("------------")
                print("Select which number you would like to search for:")
                print("1. Candidate ID by name and age")
                print("2. Candidate info by ID")
                print("3. Total Votes by candidate name")
                print("4. Total Votes by ID")
                print("5. Total Delegates by ID")
                print("6. Nevermind!")

                my_choice = int(input())

                if my_choice == 6:
                    continue
                elif my_choice == 1:
                    cand = input("Which candidate? ")
                    age = int(input("What age? "))
                    print(results.look_up_id (cur, cand, age))
                elif my_choice == 2:
                    this_id = int(input("Which ID? "))
                    print(results.look_up_info_by_id (cur, this_id))
                elif my_choice == 3:
                    cand = input("Which candidate? ")
                    print(results.look_up_total_votes_by_name(cur, cand))
                elif my_choice == 4:
                    this_id = int(input("Which ID? "))
                    print(results.look_up_total_votes_by_id (cur, this_id))
                elif my_choice == 5:
                    this_id = int(input("Which ID? "))
                    print(results.look_up_delegate_tally (cur, this_id))




    conn.close()

if __name__ == "__main__":
    main()
