from handlers.base import Base
import tornado
import db
import quotes
from decimal import Decimal

class New(Base):
    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self):
        cursor = yield self.db.execute(
                """select * from items;""")
        items = cursor.fetchall()
        self.render("new_quote.html", items=items)

class Build(Base):
    def get(self):
        self.render("build.html")

class Search(Base):
#    def get(self):
#        self.render("quote_search.html")
    @tornado.web.authenticated
    def get(self):
        self.render("mat_cost.html")

    def post(self):
        mn = self.get_argument("macola_num", None)
        l = self.get_argument("length", 0)
        w = self.get_argument("width", 0)
        q = self.get_argument("qty", 0)
        if l == "":
            l = 0
        if w == "":
            w = 0
        if q == "":
            q = 0

        if not mn:
            self.write("must enter macola number")
        else:
            cost = quotes.material_costs(mn, Decimal(l), Decimal(w), Decimal(q))
            self.write("${}".format(format(cost, '.2f')))


        
