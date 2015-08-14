from handlers.base import Base
import tornado


class List(Base):
    @tornado.gen.coroutine
    @tornado.web.authenticated
    def get(self):
        cursor = yield self.db.execute("""
        select item_no, description from items ORDER BY item_no;
        """)
        items = cursor.fetchall()
        self.render("item_list.html", items=items)


class Edit(Base):
    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self, item_no):
        # get item
        cursor = yield self.db.execute("""
        select * from items where item_no = %s;""",
        (item_no, ))
        item = cursor.fetchone()
        
        self.write(str(item))
class New(Base):
    @tornado.gen.coroutine
    @tornado.web.authenticated
    def post(self):
        item_no = self.get_argument("item_no")
        description = self.get_argument("description")
        base_price = self.get_argument("base_price", 0)
        
        cursor = yield self.db.execute("""
        insert into items(item_no, description, base_price) 
        values(%s, %s, %s);""",
        (item_no, description, base_price))
        
        self.redirect("/item/{}".format(item_no))

class Delete(Base):
    @tornado.gen.coroutine
    @tornado.web.authenticated
    def post(self, item_no):
        cursor = yield self.db.execute("""
        delete from items where item_no = %s;""", 
        (item_no,))
        self.redirect("/items")
