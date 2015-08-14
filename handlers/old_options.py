from handlers.base import Base
import tornado

class List(Base):
    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self, feature_id):
        cursor = yield self.db.execute(
                "select * from options where feature_id = %s;", 
                (feature_id,))
        options = cursor.fetchall()
        self.render("option_list.html", options=options)

class Edit(Base):
    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self, feature_id, option_id):
        cursor = yield self.db.execute(
                """select * from options 
                where feature_id = %s and 
                option_id = %s;""", 
                (feature_id, option_id))
        option = cursor.fetchone()
        self.render("option_edit.html", option=option)

    @tornado.gen.coroutine
    @tornado.web.authenticated
    def post(self, feature_id, option_id):
        description = self.get_argument("description", None)
        uom = self.get_argument("uom")
        labor_hours = self.get_argument("labor_hours")
        component = self.get_argument("component")

        cursor = yield self.db.execute(
                """update options 
                set description = %s, 
                uom = %s, 
                labor_hours = %s,
                component = %s
                where feature_id = %s 
                and option_id = %s""",
                (description,
                 uom,
                 labor_hours,
                 component,
                 feature_id,
                 option_id))
        self.redirect("/feature/{}/option/{}".format(feature_id, option_id))

class New(Base):
    @tornado.gen.coroutine
    @tornado.web.authenticated
    def post(self, feature_id):
        description = self.get_argument("description")
        uom = self.get_argument("uom")
        labor_hours = self.get_argument("labor_hours")
        component = self.get_argument("component")

        cursor = yield self.db.execute(
                """insert into options
                (feature_id, description, uom, labor_hours, component) 
                values(%s, %s, %s, %s, %s);""",
                (feature_id, description, uom, labor_hours, component))
        self.redirect("/feature/{}".format(feature_id))

class Delete(Base):
    @tornado.gen.coroutine
    @tornado.web.authenticated
    def post(self, feature_id, option_id):
        cursor = yield self.db.execute(
                """delete from options 
                where feature_id = %s and option_id = %s;""", 
                (feature_id, option_id))
        self.redirect("/feature/{}".format(feature_id))
