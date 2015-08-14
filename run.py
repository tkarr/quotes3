
import tornado.httpserver
import tornado.ioloop
import tornado.options
import momoko
import psycopg2.extras
import config
from app import Application

from tornado.options import define, options

define("port", default=8000, help="run on the given port", type=int)

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = Application()
    ioloop = tornado.ioloop.IOLoop.instance()
    app.db = momoko.Pool(
            dsn='dbname={} user={} password={} host={} port={}'.format(
                config.DATABASE_NAME,
                config.DATABASE_USER,
                config.DATABASE_PASSWORD,
                config.DATABASE_HOST,
                config.DATABASE_PORT),
            cursor_factory=psycopg2.extras.RealDictCursor,
            size=1,
            ioloop=ioloop)
    future = app.db.connect()
    ioloop.add_future(future, lambda f: ioloop.stop())
    ioloop.start()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)

    ioloop.start()
