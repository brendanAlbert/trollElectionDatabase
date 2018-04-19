# 3 additional functions to manipulate the states table
def add_state(conn, curr, name, primary_date, republican_electors, democratic_electors, num_registered_GOP,
              num_registered_dem):
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
    curr.execute(query,
                 (name, primary_date, republican_electors, democratic_electors, num_registered_GOP, num_registered_dem))
    conn.commit()


def delete_state(conn, curr, state_to_delete):
    curr.execute("""DELETE FROM State WHERE name=?""", state_to_delete)
    conn.commit()


def update_state(conn, curr, name_of_state_to_modify, new_name, primary_date, republican_electors, democratic_electors,
                 num_registered_GOP, num_registered_dem):
    cmd = """UPDATE State SET name=?, primary_or_caucus_date=?, republican_electors=?, democratic_electors=?, number_registered_republicans=?, number_registered_democrats=? WHERE name=?"""
    curr.execute(cmd, (
    new_name, primary_date, republican_electors, democratic_electors, num_registered_GOP, num_registered_dem,
    name_of_state_to_modify))
    conn.commit()
