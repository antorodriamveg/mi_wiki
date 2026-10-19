from flask import Flask, render_template, request, redirect
import psycopg2
from datetime import datetime

app = Flask(__name__)

# CONEXIÓN A POSTGRESQL EN RENDER
def get_connection():
    return psycopg2.connect(
        host="dpg-dbb4r2ui0phs73evej60-a",
        database="mi_wiki_db",
        user="mi_wiki_db_user",
        password="oHeaZLev04jymCBXnBSzY2bVdUVrh7nM",
        port="5432"
    )

# CREAR TABLA SI NO EXISTE (ejecuta una vez)
def crear_tabla_si_no_existe():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS paginas (
            id SERIAL PRIMARY KEY,
            titulo VARCHAR(255),
            contenido TEXT,
            fecha TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

# Ejecutamos la creación de tabla al iniciar la app
crear_tabla_si_no_existe()


@app.route("/")
def index():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, titulo FROM paginas ORDER BY titulo ASC")
    paginas = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("index.html", paginas=paginas)


@app.route("/pagina/<int:pagina_id>")
def ver_pagina(pagina_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT titulo, contenido, fecha FROM paginas WHERE id = %s", (pagina_id,))
    pagina = cur.fetchone()
    cur.close()
    conn.close()
    return render_template("pagina.html", pagina=pagina)


@app.route("/nueva", methods=["GET", "POST"])
def nueva_pagina():
    if request.method == "POST":
        titulo = request.form["titulo"]
        contenido = request.form["contenido"]
        fecha = datetime.now()

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO paginas (titulo, contenido, fecha) VALUES (%s, %s, %s)",
            (titulo, contenido, fecha)
        )
        conn.commit()
        cur.close()
        conn.close()

        return redirect("/")

    return render_template("nueva_pagina.html")


# Render necesita esto para correr la app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
