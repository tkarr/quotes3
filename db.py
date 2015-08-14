import config
import psycopg2.pool
import psycopg2.extras
from contextlib import contextmanager
import pymssql

macola_db = pymssql.connect(
        host=config.MACOLA_HOST,
        user=config.MACOLA_USER,
        password=config.MACOLA_PASSWORD,
        database=config.MACOLA_DATABASE,
        as_dict=True)
macola = macola_db.cursor()



class DB(object):
    '''
    DB Class

    usage:
    import db
    DB = db.DB()
    with DB.cursor() as cur:
        cur.execute("select 1;")
        x = cur.fetchone()
    print(x)
    '''

    def __init__(self):
        self.dsn = "dbname={} user={} password={} host={} port={}".format(
                config.DATABASE_NAME,
                config.DATABASE_USER,
                config.DATABASE_PASSWORD,
                config.DATABASE_HOST,
                config.DATABASE_PORT)
        self.connect()

    def connect(self):
        self.pool = psycopg2.pool.SimpleConnectionPool(
                1, 20, self.dsn, 
                cursor_factory=psycopg2.extras.RealDictCursor)

    @contextmanager
    def cursor(self):
        con = self.pool.getconn()
        con.autocommit = True
        try:
            yield con.cursor()
        finally:
            self.pool.putconn(con)
        
