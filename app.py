from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2

app = Flask(__name__)

app.secret_key = "HELIPEDIA_SECTRETA_2026"

ADMIN_PASSWORD = "Mi24Hind"

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
            imagen_url TEXT,
            imagen_url_2 TEXT,
            imagen_url_3 TEXT,
            imagen_url_4 TEXT
        );
    """)

    try:
        cur.execute("""
            ALTER TABLE modelos
            ADD COLUMN imagen_url_2 TEXT
        """)
    except:
        pass

    try:
        cur.execute("""
            ALTER TABLE modelos
            ADD COLUMN imagen_url_3 TEXT
        """)
    except:
        pass

    try:
        cur.execute("""
            ALTER TABLE modelos
            ADD COLUMN imagen_url_4 TEXT
        """)
    except:
        pass

    conn.commit()
    cur.close()
    conn.close()


crear_tablas()

# LOGIN ADMINISTRADOR
@app.route("/admin/login", methods=["GET", "POST"])
def login():

    error = None

    if request.method == "POST":

        password = request.form["password"]

        if password == ADMIN_PASSWORD:

            session["admin"] = True

            return redirect(url_for("index"))

        error = "Contraseña incorrecta"

    return render_template(
        "login.html",
        error=error
    )


# LOGOUT ADMINISTRADOR
@app.route("/admin/logout")
def logout():

    session.clear()

    return redirect(url_for("index"))

# PÁGINA PRINCIPAL
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
        cur.execute("INSERT INTO fabricantes (nombre, pais) VALUES (%s, %s)", (nombre, pais))
        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for("index"))

    return render_template("nuevo_fabricante.html")


# VER FABRICANTE
@app.route("/fabricante/<int:fabricante_id>")
def ver_fabricante(fabricante_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, nombre, pais FROM fabricantes WHERE id = %s", (fabricante_id,))
    fabricante = cur.fetchone()

    cur.execute("""
        SELECT id, nombre, anio, generacion, rol, imagen_url
        FROM modelos
        WHERE fabricante_id = %s
        ORDER BY nombre ASC
    """, (fabricante_id,))
    modelos = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("fabricante.html", fabricante=fabricante, modelos=modelos)


# NUEVO MODELO
@app.route("/modelo/nuevo/<int:fabricante_id>", methods=["GET", "POST"])
def nuevo_modelo(fabricante_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM fabricantes WHERE id = %s", (fabricante_id,))
    fabricante = cur.fetchone()

    if request.method == "POST":
        nombre = request.form["nombre"]
        rol = request.form["rol"]
        generacion = request.form["generacion"]
        anio = request.form["anio"]
        descripcion = request.form["descripcion"]
        imagen_url = request.form["imagen_url"]

        cur.execute("""
            INSERT INTO modelos (fabricante_id, nombre, rol, generacion, anio, descripcion, imagen_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (fabricante_id, nombre, rol, generacion, anio, descripcion, imagen_url))

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for("ver_fabricante", fabricante_id=fabricante_id))

    cur.close()
    conn.close()

    return render_template("nuevo_modelo.html", fabricante=fabricante)


# VER MODELO
@app.route("/modelo/<int:modelo_id>")
def ver_modelo(modelo_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT m.id, m.nombre, m.rol, m.generacion, m.anio, m.descripcion, m.imagen_url,
               f.nombre, f.pais
        FROM modelos m
        JOIN fabricantes f ON m.fabricante_id = f.id
        WHERE m.id = %s
    """, (modelo_id,))
    modelo = cur.fetchone()

    cur.close()
    conn.close()

    return render_template("modelo.html", modelo=modelo)


# BORRAR MODELO
@app.route("/modelo/borrar/<int:modelo_id>")
def borrar_modelo(modelo_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT fabricante_id FROM modelos WHERE id = %s", (modelo_id,))
    fabricante_id = cur.fetchone()[0]

    cur.execute("DELETE FROM modelos WHERE id = %s", (modelo_id,))
    conn.commit()

    cur.close()
    conn.close()

    return redirect(url_for("ver_fabricante", fabricante_id=fabricante_id))


# EDITAR MODELO (ÚNICA FUNCIÓN, SIN DUPLICADOS)
@app.route("/modelo/editar/<int:modelo_id>", methods=["GET", "POST"])
def editar_modelo(modelo_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, fabricante_id, nombre, rol, generacion, anio, descripcion, imagen_url
        FROM modelos
        WHERE id = %s
    """, (modelo_id,))
    modelo = cur.fetchone()

    if request.method == "POST":
        nombre = request.form["nombre"]
        rol = request.form["rol"]
        generacion = request.form["generacion"]
        anio = request.form["anio"]
        descripcion = request.form["descripcion"]
        imagen_url = request.form["imagen_url"]

        cur.execute("""
            UPDATE modelos
            SET nombre=%s, rol=%s, generacion=%s, anio=%s, descripcion=%s, imagen_url=%s
            WHERE id=%s
        """, (nombre, rol, generacion, anio, descripcion, imagen_url, modelo_id))

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for("ver_modelo", modelo_id=modelo_id))

    cur.close()
    conn.close()

    return render_template("editar_modelo.html", modelo=modelo)


# BORRAR FABRICANTE (CON PROTECCIÓN)
@app.route("/fabricante/borrar/<int:fabricante_id>")
def borrar_fabricante(fabricante_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM modelos WHERE fabricante_id = %s", (fabricante_id,))
    cantidad_modelos = cur.fetchone()[0]

    if cantidad_modelos > 0:
       cur.close()
       conn.close()

       return render_template(
           "error_borrar_fabricante.html",
           fabricante_id=fabricante_id
       )

    cur.execute("DELETE FROM fabricantes WHERE id = %s", (fabricante_id,))
    conn.commit()

    cur.close()
    conn.close()

    return redirect(url_for("index"))


# EDITAR FABRICANTE
@app.route("/fabricante/editar/<int:fabricante_id>", methods=["GET", "POST"])
def editar_fabricante(fabricante_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, nombre, pais FROM fabricantes WHERE id = %s", (fabricante_id,))
    fabricante = cur.fetchone()

    if request.method == "POST":
        nombre = request.form["nombre"]
        pais = request.form["pais"]

        cur.execute("""
            UPDATE fabricantes
            SET nombre = %s, pais = %s
            WHERE id = %s
        """, (nombre, pais, fabricante_id))

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for("ver_fabricante", fabricante_id=fabricante_id))

    cur.close()
    conn.close()

    return render_template("editar_fabricante.html", fabricante=fabricante)


# BUSCADOR
@app.route("/buscar")
def buscar():

    termino = request.args.get("q", "")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, nombre, pais
        FROM fabricantes
        WHERE nombre ILIKE %s
        ORDER BY nombre
    """, (f"%{termino}%",))

    fabricantes = cur.fetchall()

    cur.execute("""
        SELECT id, nombre
        FROM modelos
        WHERE nombre ILIKE %s
        ORDER BY nombre
    """, (f"%{termino}%",))

    modelos = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "buscar.html",
        termino=termino,
        fabricantes=fabricantes,
        modelos=modelos
    )

# Render necesita esto para correr la app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
    
