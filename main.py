import os
from flask import Flask, request
import pandas as pd
import sqlite3
from datetime import datetime as dt

app = Flask(__name__)

# 40 habitaciones reales (sin 113)
HAB = ["101","102","103","104","105","106","107","108","109","110","111","112","114","115",
       "201","202","203","204","205","206","207","208","209",
       "301","302","303","304","305","306","307","308","309",
       "401","402","403","404","405","406","407","408","409","501","Suite"]

DB = "reservas.db"
conn = sqlite3.connect(DB)
conn.execute("CREATE TABLE IF NOT EXISTS r(hab,huesped,tel,cin,cout)")
conn.close()

@app.route("/",methods=["GET","POST"])
def home():
    msg = ""
    if request.method=="POST":
        if "file" in request.files and request.files["file"].filename:
            pd.read_csv(request.files["file"]).to_sql("r",sqlite3.connect(DB),if_exists="append",index=False)
            msg="CSV subido ✓"
        else:
            sqlite3.connect(DB).execute("INSERT INTO r VALUES(?,?,?,?,?)",
                (request.form["hab"],request.form["huesped"],request.form.get("tel",""),
                 request.form["cin"],request.form["cout"])).close()
            msg="Reserva añadida ✓"

    res = sqlite3.connect(DB).execute("SELECT * FROM r").fetchall()
    precio = 85 if dt.now().weekday()<5 else 106

    return f"""
    <h1>HotelBoost AI – 49€/mes</h1>
    <p style="color:green;font-size:20px"><b>{msg}</b></p>
    <form method=post enctype=multipart/form-data><input type=file name=file accept=.csv,.xlsx> <button>Subir CSV</button></form>
    <hr>
    <form method=post>
      Hab: <select name=hab>{''.join(f'<option>{h}</option>'for h in HAB)}</select>
      Huésped: <input name=huesped required> Tel: <input name=tel>
      In: <input type=date name=cin required> Out: <input type=date name=cout required>
      <button>Añadir reserva</button>
    </form>
    <h2>Precio mañana: {precio}€</h2>
    <table border=1><tr><th>Hab</th><th>Huésped</th><th>Tel</th><th>In</th><th>Out</th></tr>
    {''.join(f'<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td>{r[4]}</td></tr>'for r in res)}
    </table>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",8080)))
