from handlers.base import Base
import tornado

class List(Base):
    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self, edit_id=None):
        cursor = yield self.db.execute(
                """select * from options
                   where parent_id is null
		   order by option_id asc;""")
        options = cursor.fetchall()
        for o in options:
            o = yield self.get_children(o)
        if edit_id:
            cursor= yield self.db.execute(
                """select * from options
                where option_id = %s;""",
                (edit_id,))
            edit_option = cursor.fetchone()
        else:
            edit_option = None
        self.render("option_list.html", options=options, edit_option=edit_option, render_tree=self.render_tree)

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
    

    def render_tree(self, options):
        ''' returns html for options tree '''
        tree = """<ol class="tree" id="option_list">"""

        def recurse(option):
            nonlocal tree
            tree += """<li class="tree">
                            <label for="{0}">{1}
                                <a href="/option/{0}"><span class="glyphicon glyphicon-pencil"></span></a>
                                <a id="{0}_add" class="add_sub_option" href="#" style="color:green"><span class="glyphicon glyphicon-plus"></span></a>
                                <a href="/option/{0}/delete" style="color:red"><span class="glyphicon glyphicon-remove"></span></a>
                            </label>
                            <input type="checkbox" id="{0}" /> 
                     <ol id="{0}_children">""".format(option['option_id'], option['description'])
            for c in option['children']:
                recurse(c)
            tree += "</ol></li>"

        for o in options:
            recurse(o)

        tree += "</ol>"
        return tree

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def post(self, option_id):
        description = self.get_argument("description", None)
        uom = self.get_argument("uom", None)
        stock_no = self.get_argument("stock_no", None)
        
        cursor = yield self.db.execute(
                """update options set 
                    description = %s, 
                    uom = %s,
                    stock_no = %s
                    where option_id= %s""",
                (description.upper(), uom, stock_no, option_id))
        self.redirect("/option/{}".format(option_id))

class New(Base):
    @tornado.web.authenticated
    @tornado.gen.coroutine
    def post(self):
        description = self.get_argument("description")
        parent_id = self.get_argument("parent_id", None)
        cursor = yield self.db.execute(
                """insert into options(description, parent_id) 
                values(%s, %s) returning option_id;""",
                (description, parent_id))
        option_id = cursor.fetchone()['option_id']
        self.redirect("/option/{}".format(option_id))

class Delete(Base):
    def get(self, option_id):
        self.render("delete_option.html", option_id=option_id)

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def post(self, option_id):
        yield self.delete_children(option_id)
        cursor = yield self.db.execute(
                "delete from options where option_id = %s;",
                (option_id,))
        self.redirect("/options")

    @tornado.gen.coroutine
    def delete_children(self, option_id):
        ''' recursively delete children of option_id '''
        cursor = yield self.db.execute("""
            DELETE FROM options WHERE parent_id = %s
            RETURNING option_id;""",
            (option_id,))
        children = cursor.fetchall()
        for c in children:
            yield self.delete_children(c['option_id'])



