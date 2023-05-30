from itemadapter import ItemAdapter
import sqlite3


class FincaraizPipeline:
    def __init__(self):
        self.con = sqlite3.connect("fincaRaiz.db")
        self.cur = self.con.cursor()
        self.cur.execute(
            """CREATE TABLE IF NOT EXISTS houses(
                id INTEGER, 
                rooms INTEGER, 
                bathrooms INTEGER, 
                parking BOOLEAN, 
                area INTEGER, 
                stratum INTEGER, 
                price INTEGER, 
                CONSTRAINT primary_key_constraint PRIMARY KEY (id)
            )"""
        )

    def process_item(self, item, spider):
        self.cur.execute(
            """INSERT INTO houses (rooms, bathrooms, parking, area, stratum, price) VALUES (?, ?, ?, ?, ?, ?)""",
            (
                int(item["rooms"]),
                int(item["bathrooms"]),
                item["parking"],
                int(item["area"]),
                int(item["stratum"]),
                int(item["price"]),
            ),
        )

        self.con.commit()
        return item
