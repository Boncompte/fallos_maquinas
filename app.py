from flask import Flask, render_template, request, redirect, url_for, session
from supabase import create_client, Client
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Cambia esto por algo más seguro

# Configuración de Supabase
SUPABASE_URL = "TU_URL_DE_SUPABASE"
SUPABASE_KEY = "TU_CLAVE_API_DE_SUPABASE"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Página de inicio (login)
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Autenticación en Supabase
        try:
            user = supabase.auth.sign_in_with_password({"email": email, "password": password})
            session["user"] = user["user"]
            session["role"] = user["data"]["role"]  # Asume que el rol está en los datos del usuario
            return redirect(url_for("consulta"))
        except Exception as e:
            return render_template("login.html", error="Login fallido. Por favor, revisa tus credenciales.")

    return render_template("login.html")

# Página de consulta (disponible para todos)
@app.route("/consulta")
def consulta():
    if "user" not in session:
        return redirect(url_for("login"))

    # Buscar datos en la tabla
    datos = supabase.table("fallos_maquinas").select("*").execute()
    return render_template("consulta.html", fallos=datos["data"])

# Página de administración (solo para admin)
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if "user" not in session or session.get("role") != "admin":
        return redirect(url_for("consulta"))

    if request.method == "POST":
        codigo = request.form["codigo"]
        causa = request.form["causa"]
        consecuencia = request.form["consecuencia"]
        accion = request.form["accion"]

        # Insertar datos en la tabla
        supabase.table("fallos_maquinas").insert({
            "codigo_fallo": codigo,
            "causa": causa,
            "consecuencia": consecuencia,
            "accion_correctiva": accion
        }).execute()

        return redirect(url_for("admin"))

    # Obtener datos para mostrarlos
    datos = supabase.table("fallos_maquinas").select("*").execute()
    return render_template("admin.html", fallos=datos["data"])

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
