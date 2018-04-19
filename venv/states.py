# 3 additional functions to manipulate the states table
def add_state(conn, curr, ):
    # Add the book The Giver Blue by Lois Lowry with the barcode 3331642
    title = "The Giver Blue"
    author = "Lois Lowry"
    barcode = 3331642
    cmd = """
    INSERT INTO Book(barcode, title, author)
    VALUES(?, ?, ?)
    """
    curr.execute(cmd, (barcode, title, author))
    conn.commit()
