from handlers.base import Base
import tornado
import db
import quotes
from decimal import Decimal

class New(Base):
    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self):
        self.redirect("/quote/1234")

class Edit(Base):
    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self, quote_no):
        cursor = yield self.db.execute(
                """select * from items;""")
        items = cursor.fetchall()
        self.render("new_quote.html", items=items, quote_no=quote_no)

class NewItem(Base):
    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self, quote_no):
        item_no = self.get_argument("item_no")

        # get enabled options
        cursor = yield self.db.execute("""
            SELECT * FROM enabled_options where item_no = %s;""",
            (item_no,))
        enabled_options = [x['option_id'] for x in cursor.fetchall()]

        cursor = yield self.db.execute("""
            SELECT * FROM options where parent_id is null
            order by option_id asc;""")
        options = cursor.fetchall()
        item_options = []
        for o in options:
            if o['option_id'] in enabled_options:
                o = yield self.get_children(o, enabled_options, check_enabled=True)
                item_options.append(o)

        cursor = yield self.db.execute("""
            SELECT * FROM items WHERE item_no = %s;""",
            (item_no,))
        item = cursor.fetchone()
        self.render("new_item.html", item=item, render_tree=self.render_tree, options=item_options)

    @tornado.gen.coroutine
    def get_children(self, option, enabled_options, check_enabled=False):
        '''
        if check_enabled is True, it will check if option_id is in enabled_options.
        Since enabled_options only work two levels deep, the subsequent recursions
        do not switch check_enabled to True
        '''
        cursor = yield self.db.execute("""
            SELECT * FROM options
            WHERE parent_id = %s
	    order by option_id asc;""",
            (option['option_id'],))
        children = cursor.fetchall()
        option['children'] = []
        for child in children:
            if child['option_id'] in enabled_options or check_enabled == False:
                child = yield self.get_children(child, enabled_options)
                option['children'].append(child)
        return option
    
    def render_tree(self, options):
        ''' returns html for options tree '''
        tree = """<ul class="tree" id="option_list">"""

        def recurse(option):
            nonlocal tree
            tree += """<li class="tree" style="padding: 10px;">
                            <div class="form-group">
                            <input type="checkbox" id="{0}" class="option"/> 
                            </div>
                            <div class="form-group">
                            <textarea rows="1" class="form-control">{1}</textarea>
                            </div>""".format(option['option_id'], option['description'])
            if option['uom'] == "IN":
                tree += """<div class="form-group">&nbsp;&nbsp;<input type="text" class="form-control length" placeholder="length in inches"></div>"""
            elif option['uom'] == "EA":
                tree += """<div class="form-group">&nbsp;&nbsp;<input type="text" class="form-control qty" placeholder="quantity"></div>"""
          
            tree += """<div style="float: right; clear: both; position: absolute; right: 150px;" class="form-group">
                        <div class="input-group">
                            <span class="input-group-addon">$</span>
                            <input type="text" class="form-control" value="1234">
                        </div>
                       </div>"""
            tree += """<ul id="{0}_children" class="child">""".format(option['option_id'])
            for c in option['children']:
                recurse(c)
            tree += "</ul></li>"

        for o in options:
            recurse(o)

        tree += "</ul>"
        return tree



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


        
