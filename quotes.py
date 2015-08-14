from decimal import Decimal
import db
macola = db.macola
db = db.DB()

# labor hours per linear inch



# if sink in name 
#SINK = (((((L*H)*2) * ((W*H)*2) + (L * W))/144) * Decimal(3.15)) * std_cost


def material_costs(component, length, width, qty):
    macola.execute("""
        SELECT uom FROM IMITMIDX_SQL where item_no = %s;""",
        (component,))
    macola_uom = macola.fetchone()['uom']

    if component.endswith("P") or component.endswith("PL"):
        macola.execute("""
            SELECT 
            SUM((BMPRDSTR_SQL.qty_per_par * IMINVLOC_SQL.std_cost)) as cost
            FROM 
            BMPRDSTR_SQL INNER JOIN IMINVLOC_SQL ON
            BMPRDSTR_SQL.comp_item_no = IMINVLOC_SQL.item_no AND
            BMPRDSTR_SQL.loc = IMINVLOC_SQL.loc
            WHERE BMPRDSTR_SQL.item_no = %s""",
            (component,))
        print("phantom")
        return macola.fetchone()['cost'] * qty
    else:
        print("not phantom")
        macola.execute("""
            SELECT IMINVLOC_SQL.std_cost FROM 
            IMITMIDX_SQL INNER JOIN IMINVLOC_SQL
            ON IMITMIDX_SQL.item_no = IMINVLOC_SQL.item_no
            AND IMITMIDX_SQL.loc = IMINVLOC_SQL.loc
            WHERE IMINVLOC_SQL.item_no = %s;""",
            (component,))
        std_cost = macola.fetchone()['std_cost']

        if macola_uom == "LB":
            lbpersqft = {
                    "100011" : Decimal(1.49), #20g
                    "100013" : Decimal(2.02), #18g
                    "100015" : Decimal(2.51), #16g
                    "100017" : Decimal(3.15), #14g
                    "100019" : Decimal(4.43)} #12g
            sqft = Decimal((length / 12) * (width / 12))
            try:
                lbs = Decimal(sqft * lbpersqft[component])
                return Decimal(std_cost * lbs)
            except KeyError:
                return 0
        elif macola_uom == "SF":
            sqft = Decimal((length / 12) * (width / 12))
            return std_cost * sqft
        elif macola_uom == "EA":
            return Decimal(qty * std_cost)
        elif macola_uom == "FT":
            return Decimal(Decimal((length / 12)) * std_cost)


def new_feature(description):
    with db.cursor() as cur:
        cur.execute("""
            INSERT INTO features(description)
            VALUES (%s)
            RETURNING feature_id;""",
            (description,))
        return cur.fetchone()['feature_id']

def new_option(feature_id, description, uom, 
        component, labor_hours=0, length=0, width=0, height=0, qty=0):
    with db.cursor() as cur:
        cur.execute("""
            INSERT INTO options(feature_id, description, uom, labor_hours,
            length, width, height, qty, component)
            VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING option_id;""",
            (feature_id, description, uom, component, labor_hours, 
                length, width, height, qty))
        return cur.fetchone()['option_id']


class Feature(object):
    '''
    attributes
    -----
    feature_id
    description
    '''
    def __init__(self, feature_id):
        with db.cursor() as cur:
            cur.execute(
                """SELECT * FROM features
                where feature_id = %s;""", 
                (feature_id,))
            results = cur.fetchone()
        for k, v in results.items():
            setattr(self, k, v)

    def available_options(self):
        with db.cursor()as cur:
            cur.execute(
                """SELECT option_id FROM options
                WHERE feature_id = %s;""",
                (self.feature_id,))
            return [Option(x['option_id']) for x in cur.fetchall()]





class Option(object):
    '''
    option_id
    feature_id
    description
    uom
    macola_uom - set when running material_costs()
    '''
    def __init__(self, option_id):
        with db.cursor() as cur:
            cur.execute(
                """SELECT * FROM options 
                where option_id = %s;""", 
                (option_id,))
            results = cur.fetchone()
        for k, v in results.items():
            setattr(self, k, v)

        # macola uom that determines which formula to use
        # ex. macola_uom = "LBS" convert SF to lbs 
        macola.execute("""
            SELECT uom FROM IMITMIDX_SQL where item_no = %s;""",
            (self.component,))
        self.macola_uom = macola.fetchone()['uom']

    def material_costs(self):
        if self.component.endswith("P") or self.component.endswith("PL"):
            macola.execute("""
                SELECT 
                SUM((BMPRDSTR_SQL.qty_per_par * IMINVLOC_SQL.std_cost)) as cost                FROM 
                BMPRDSTR_SQL INNER JOIN IMINVLOC_SQL ON
                BMPRDSTR_SQL.comp_item_no = IMINVLOC_SQL.item_no AND
                BMPRDSTR_SQL.loc = IMINVLOC_SQL.loc
                WHERE BMPRDSTR_SQL.item_no = %s""",
                (self.component,))
            print("phantom")
            return macola.fetchone()['cost'] * self.qty
        else:
            print("not phantom")
            macola.execute("""
                SELECT IMINVLOC_SQL.std_cost FROM 
                IMITMIDX_SQL INNER JOIN IMINVLOC_SQL
                ON IMITMIDX_SQL.item_no = IMINVLOC_SQL.item_no
                AND IMITMIDX_SQL.loc = IMINVLOC_SQL.loc
                WHERE IMINVLOC_SQL.item_no = %s;""",
                (self.component,))
            std_cost = macola.fetchone()['std_cost']
            if self.macola_uom == "LB":
                lbpersqft = {
                     "100011" : Decimal(1.49), #20g
                     "100013" : Decimal(2.02), #18g
                     "100015" : Decimal(2.51), #16g
                     "100017" : Decimal(3.15), #14g
                     "100019" : Decimal(4.43)} #12g
                sqft = Decimal((self.length / 12) * (self.width / 12))
                try:
                    lbs = Decimal(sqft * lbpersqft[self.component])
                    return Decimal(std_cost * lbs)
                except KeyError:
                    return 0
            elif self.macola_uom == "SF":
                sqft = Decimal((self.length / 12) * (self.width / 12))
                return std_cost * sqft
            elif self.macola_uom == "EA":
                return Decimal(self.qty * std_cost)
            elif self.macola_uom == "FT":
                return Decimal(Decimal((self.length / 12)) * std_cost)

    def labor_costs(self):
        return Decimal(self.labor_hours) * Decimal(16) # labor_rate guess

    def cost(self):
        return (material_costs() + labor_costs())
