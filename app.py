
from flask import Flask, render_template, request, redirect, url_for
import psycopg2

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

# CREAR TABLAS SI NO EXISTEN
def crear_tablas():
    conn = get_connection()
    cur = conn.cursor()

    # Fabricantes
    cur.execute("""
        CREATE TABLE IF NOT EXISTS fabricantes (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(255),
            pais VARCHAR(255)
        );
    """)

    # Modelos (aeronaves)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS modelos (
            id SERIAL PRIMARY KEY,
            fabricante_id INTEGER REFERENCES fabricantes(id),
            nombre VARCHAR(255),
            rol VARCHAR(255),
            generacion INTEGER,
            anio INTEGER,
            descripcion TEXT,
            imagen_url TEXT
        );
    """)

    conn.commit()
    cur.close()
    conn.close()

# Ejecutamos la creación de tablas al iniciar la app
crear_tablas()


# PÁGINA PRINCIPAL: lista de fabricantes
@app.route("/")
def index():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre, pais FROM fabricantes ORDER BY nombre ASC")
    fabricantes = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("fabricantes.html", fabricantes=fabricantes)


# NUEVO FABRICANTE
@app.route("/fabricante/nuevo", methods=["GET", "POST"])
def nuevo_fabricante():
    if request.method == "POST":
        nombre = request.form["nombre"]
        pais = request.form["pais"]

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO fabricantes (nombre, pais) VALUES (%s, %s)",
            (nombre, pais)
        )
        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for("index"))

    return render_template("nuevo_fabricante.html")


# VER FABRICANTE (lista de modelos de ese fabricante)
@app.route("/fabricante/<int:fabricante_id>")
def ver_fabricante(fabricante_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, nombre, pais FROM fabricantes WHERE id = %s", (fabricante_id,))
    fabricante = cur.fetchone()

    cur.execute("""
        SELECT id, nombre, anio, generacion, rol
        FROM modelos
        WHERE fabricante_id = %s
        ORDER BY nombre ASC
    """, (fabricante_id,))
    modelos = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("fabricante.html", fabricante=fabricante, modelos=modelos)


# NUEVO MODELO (AERONAVE) PARA UN FABRICANTE
@app.route("/modelo/nuevo/<int:fabricante_id>", methods=["GET", "POST"])
def nuevo_modelo(fabricante_id):
    if request.method == "POST":
        nombre = request.form["nombre"]
        rol = request.form["rol"]
        generacion = request.form["generacion"]
        anio = request.form["anio"]
        descripcion = request.form["descripcion"]
        imagen_url = request.form["imagen_url"]

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO modelos (fabricante_id, nombre, rol, generacion, anio, descripcion, imagen_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (fabricante_id, nombre, rol, generacion, anio, descripcion, imagen_url))
        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for("ver_fabricante", fabricante_id=fabricante_id))

    return render_template("nuevo_modelo.html", fabricante_id=fabricante_id)


# VER FICHA TÉCNICA DE UN MODELO
@app.route("/modelo/<int:modelo_id>")
def ver_modelo(modelo_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT m.id, m.nombre, m.rol, m.generacion, m.anio, m.informacion, m.imagen_url,
               f.nombre, f.pais
        FROM modelos m
        JOIN fabricantes f ON m.fabricante_id = f.id
        WHERE m.id = %s
    """, (modelo_id,))
    modelo = cur.fetchone()

    cur.close()
    conn.close()

    return render_template("modelo.html", modelo=modelo)


# Render necesita esto para correr la app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
