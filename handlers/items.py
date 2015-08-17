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

    @tornado.gen.coroutine
    @tornado.web.authenticated
    def post(self):
        item_no = self.get_argument("item_no")
        description = self.get_argument("description")
        base_price = self.get_argument("base_price", 0)
        profit = self.get_argument("profit", 0)

        cursor = yield self.db.execute("""
        insert into items(item_no, description, base_price, profit) 
        values(%s, %s, %s, %s);""",
        (item_no, description, base_price, profit))
        self.redirect("/item/{}".format(item_no))


class Edit(Base):
    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self, item_no):
        # get item
        cursor = yield self.db.execute("""
        select * from items where item_no = %s;""",
        (item_no, ))
        item = cursor.fetchone()
        
        cursor = yield self.db.execute("""
            select * from enabled_options where item_no = %s;""",
            (item_no,))
        enabled_options = cursor.fetchall()

        cursor = yield self.db.execute(
                """select * from options
                   where parent_id is null
		   order by option_id asc;""")
        options = cursor.fetchall()
        for o in options:
            if o['option_id'] in [x['option_id'] for x in enabled_options]:
                o['enabled'] = True
            else:
                o['enabled'] = False
            o = yield self.get_children(o)
        self.render("item_edit.html", item=item, options=options, render_tree=self.render_tree)        

    @tornado.gen.coroutine
    def get_children(self, option):
        cursor = yield self.db.execute("""
            SELECT * FROM options
            WHERE parent_id = %s
	    order by option_id asc;""",
            (option['option_id'],))
        option['children'] = cursor.fetchall()
        for child in option['children']:
            child['enabled'] = False
            child = yield self.get_children(child)
        return option
    
    def render_tree(self, options):
        ''' returns html for options tree '''
        tree = """<ul id="option_list">"""
        for o in options:
            tree += """<li>
                            <label for="{0}">{1}
                            </label>
                            <input type="checkbox" id="{0}" />
                            <ul id="{0}_children">""".format(o['option_id'], o['description'])
            for c in o['children']:
                tree += """
                    <li>
                        <label for = "{0}">{1}
                        </label>
                        <input type="checkbox" id="{0}" />
                    </li>""".format(c['option_id'], c['description'])
            tree += "</ul></li>"

        tree += "</ul>"
        return tree



class Delete(Base):
    @tornado.gen.coroutine
    @tornado.web.authenticated
    def post(self, item_no):
        cursor = yield self.db.execute("""
        delete from items where item_no = %s;""", 
        (item_no,))
        cursor = yield self.db.execute("""
        delete from enabled_options where item_no = %s;""",
        (item_no,))
        self.redirect("/items")
