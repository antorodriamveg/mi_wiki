from flask import Flask, render_template, request, redirect
import mysql.connector
from datetime import datetime

app = Flask(__name__)

def obtener_conexion():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="wiki"
    )

@app.route("/")
def index():
    con = obtener_conexion()
    cur = con.cursor()
    cur.execute("SELECT id, titulo FROM paginas ORDER BY titulo ASC")
    paginas = cur.fetchall()
    con.close()
    return render_template("index.html", paginas=paginas)

@app.route("/pagina/<int:pagina_id>")
def ver_pagina(pagina_id):
    con = obtener_conexion()
    cur = con.cursor()
    cur.execute("SELECT titulo, contenido, fecha FROM paginas WHERE id = %s", (pagina_id,))
    pagina = cur.fetchone()
    con.close()
    return render_template("pagina.html", pagina=pagina)

@app.route("/nueva", methods=["GET", "POST"])
def nueva_pagina():
    if request.method == "POST":
        titulo = request.form["titulo"]
        contenido = request.form["contenido"]
        fecha = datetime.now()

        con = obtener_conexion()
        cur = con.cursor()
        cur.execute("INSERT INTO paginas (titulo, contenido, fecha) VALUES (%s, %s, %s)",
                    (titulo, contenido, fecha))
        con.commit()
        con.close()

        return redirect("/")

    return render_template("nueva_pagina.html")

app.run(debug=True)
