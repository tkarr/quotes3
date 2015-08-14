import db
db = db.DB()


def list():
    ''' lists all options '''
    options = []
    def children(option):
        ''' recursively adds children to an option '''
        with db.cursor() as cur:
            cur.execute("""
            SELECT * FROM options
            WHERE parent_id = %s;""",
            (option['option_id'],))
            option['children'] = cur.fetchall()
        for child in option['children']:
            child = children(child)
        return option

    with db.cursor() as cur:
        cur.execute("""
            SELECT * FROM options
            WHERE parent_id IS NULL;""")
        options = cur.fetchall()
        for o in options:
            o = children(o)
    return options


def add(description, uom=None, component=None, parent_id=None):
    with db.cursor() as cur:
        cur.execute(
            """
            INSERT INTO options(description, uom, component, parent_id)
            VALUES(%s, %s, %s, %s)
            RETURNING option_id;""",
            (description, uom, component, parent_id))
        return cur.fetchone()['option_id']

if __name__ == "__main__":
    LEVEL = 0

    def print_op(o):
        global LEVEL
        current_level = LEVEL
        LEVEL += 1
        if not o['children']:
            LEVEL = current_level
        for child in o['children']:
            dashes = "|"
            for i in range(0, LEVEL):
                dashes += "---"
            print(dashes, child['option_id'], child['description'])
            print_op(child)

    options = list()
    for option in options:
        print(option['option_id'], option['description'])
        print_op(option)
        LEVEL = 0
