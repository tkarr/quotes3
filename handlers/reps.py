from handlers.base import Base
import tornado
import db

class List(Base):
    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self):
        cursor = yield self.db.execute("""
            SELECT * FROM reps;""")
        result = cursor.fetchall()
        reps = []
        for row in result:
            rep = dict(row)
            db.macola.execute("""
                SELECT * FROM ARSLMFIL_SQL
                WHERE slspsn_no = %s;""",
                (row['rep_no'],))
            rep.update(db.macola.fetchone())
            reps.append(rep)

        self.render("rep_list.html", reps=reps)

class New(Base):
    @tornado.web.authenticated
    @tornado.gen.coroutine
    def post(self):
        rep_no = self.get_argument("rep_no")[0:3]
        zip_index = self.get_argument("zip_index")
        zip_dict = dict()
        for i in range(0, int(zip_index) + 1):
            zip_dict[i] = (self.get_argument("zip_{}_start".format(i)),
                           self.get_argument("zip_{}_end".format(i)))

        discount = self.get_argument("discount")
        if not discount:
            discount = 0

        zip_thing = '{'
        for k, v in zip_dict.items():
            zip_thing += "{"
            zip_thing += '"{}", "{}"'.format(v[0], v[1]) 
            zip_thing += "},"
        zip_thing = zip_thing[0:-1] 
        zip_thing += '}'
        
        cursor = yield self.db.execute("""
            INSERT INTO reps(rep_no, zip_codes, discount)
            VALUES (%s, %s, %s);""",
            (rep_no, zip_thing, discount))

        self.redirect("/rep/{}".format(rep_no))

class Zip(Base):
    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self, zip_code):
        rep = yield self.which_rep(zip_code)
        self.write(str(rep))

class Delete(Base):
    @tornado.web.authenticated
    @tornado.gen.coroutine
    def post(self, rep_no):
        cursor = yield self.db.execute("""
            DELETE FROM reps WHERE rep_no = %s;""",
            (rep_no,))
        self.redirect('/reps')


class Edit(Base):
    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self, rep_no):
        try:
            cursor = yield self.db.execute("""
                    SELECT * FROM reps WHERE rep_no = %s;""",
                    (rep_no,))
            rep = dict(cursor.fetchone())
        
            db.macola.execute("""
                SELECT * FROM ARSLMFIL_SQL
                WHERE slspsn_no = %s;""",
                (rep_no,))
            rep.update(db.macola.fetchone())

            self.render("rep_edit.html", rep=rep)
        except:
            self.write("rep not in quote database")

class Autocomplete(Base):
    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self):
        query = self.get_argument("query")
        db.macola.execute("""
            SELECT DISTINCT slspsn_no, slspsn_name FROM ARSLMFIL_SQL
            WHERE slspsn_no LIKE %s;""",
            ("%{}%".format(query)))
        all_reps = db.macola.fetchall()

        cursor = yield self.db.execute("""
            SELECT rep_no FROM reps;""")
        existing_reps = [x['rep_no'] for x in cursor.fetchall()]

        reps = [x['slspsn_no'] + " - " + x['slspsn_name'] for x in all_reps if x['slspsn_no'] not in existing_reps]
        self.write(tornado.escape.json_encode({"suggestions": sorted(reps)}))
        
