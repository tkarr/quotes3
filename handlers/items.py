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
            o = yield self.get_children(o)
        for o in options:
            if o['option_id'] in [x['option_id'] for x in enabled_options]:
                o['enabled'] = True
                o['sort_index'] = [x['sort_index'] for x in enabled_options if x['option_id'] == o['option_id']][0]
            else:
                o['enabled'] = False
                o['sort_index'] = 999
            for c in o['children']:
                if c['option_id'] in [x['option_id'] for x in enabled_options]:
                    c['enabled'] = True
                    c['sort_index'] = [x['sort_index'] for x in enabled_options if x['option_id'] == c['option_id']][0]
                else:
                    c['enabled'] = False
                    c['sort_index'] = 999
        options = sorted(options, key=lambda k: k['sort_index'])
        self.render("item_edit.html", item=item, options=options)        

    @tornado.gen.coroutine
    def get_children(self, option):
        cursor = yield self.db.execute("""
            SELECT * FROM options
            WHERE parent_id = %s
	    order by option_id asc;""",
            (option['option_id'],))
        option['children'] = cursor.fetchall()
        for child in option['children']:
            child = yield self.get_children(child)
        return option
    

    @tornado.gen.coroutine
    @tornado.web.authenticated
    def post(self, item_no):
        description = self.get_argument("description")
        base_price = self.get_argument("base_price", 0)
        profit = self.get_argument("profit", 0)

        try:
            enabled_options = self.request.arguments['enabled_options[]']
        except:
            enabled_options = []

        cursor = yield self.db.execute("""
            SELECT * FROM enabled_options where item_no = %s;""",
            (item_no,))
        currently_enabled_options = [x['option_id'] for x in cursor.fetchall()]

        # delete from enabled options if unselected
        for o in currently_enabled_options:
            if o not in [int(x.decode()) for x in enabled_options]:
                cursor = yield self.db.execute("""
                        DELETE FROM enabled_options
                        WHERE item_no = %s AND option_id = %s;""",
                        (item_no, o))
#                # delete enabled options for removed level 1 option
#                cursor = yield self.db.execute("""
#                        DELETE FROM enabled_options
#                        WHERE item_no = %s and parent_id = %s;""",
#                        (item_no, f))
#
#        # for each enabled level 1 option, get list of enabled children
        for option_id in enabled_options:
#
            cursor = yield self.db.execute("""
                INSERT INTO enabled_options
                (item_no, option_id)
                SELECT %s, %s
                WHERE
                    NOT EXISTS (
                        SELECT item_no, option_id FROM enabled_options 
                        WHERE item_no = %s AND option_id = %s
                            );""",
                (item_no, option_id.decode(), item_no, option_id.decode()))
#            
#            option_name = "{}_options[]".format(feature_id.decode())
#            enabled_options = self.request.arguments[option_name]
#
#            cursor = yield self.db.execute("""
#                        SELECT * FROM enabled_options WHERE item_no = %s AND feature_id = %s;""",
#                        (item_no, feature_id.decode()))
#            currently_enabled_options = [x['option_id'] for x in cursor.fetchall()]
#
#            # delete from enabled options if unselected
#            for o in currently_enabled_options:
#                if o not in [int(x.decode()) for x in enabled_options]:
#                    cursor = yield self.db.execute("""
#                            DELETE FROM enabled_options
#                            WHERE item_no = %s AND feature_id = %s
#                            AND option_id = %s;""",
#                            (item_no, feature_id.decode(), o))
#
#
#
#
#            for option_id in enabled_options:
#                cursor = yield self.db.execute("""
#                    INSERT INTO enabled_options
#                    (item_no, feature_id, option_id)
#                    SELECT %s, %s, %s
#                    WHERE
#                        NOT EXISTS (
#                            SELECT item_no, feature_id, option_id FROM enabled_options 
#                            WHERE item_no = %s AND feature_id = %s AND option_id = %s
#                            );""",
#                    (item_no, feature_id.decode(), option_id.decode(), 
#                        item_no, feature_id.decode(), option_id.decode()))
#
#
        cursor = yield self.db.execute("""
        update items set description = %s, base_price = %s, profit = %s
        where item_no = %s;""",
        (description, base_price, profit, item_no))

        self.redirect("/item/{}".format(item_no))




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


class Sort(Base):
    @tornado.gen.coroutine
    @tornado.web.authenticated
    def post(self, item_no):
        for option_id, sort_index in self.request.arguments.items():
            if option_id != "_xsrf":
                try:
                    cursor = yield self.db.execute("""
                    update enabled_options
                    set sort_index = %s
                    where option_id = %s
                    and item_no = %s;""",
                    (sort_index[0].decode(),
                     option_id,
                     item_no))
                except:
                    pass
