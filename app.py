from flask import Flask, render_template, request, redirect, url_for, session
from supabase import create_client, Client
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Cambia esto por algo más seguro

# Configuración de Supabase
SUPABASE_URL = "https://mkajuzdzzljrykquvkje.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1rYWp1emR6emxqcnlrcXV2a2plIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzU1OTg5ODksImV4cCI6MjA1MTE3NDk4OX0.D_AYE0rawTVdpJzf5JHpBVZ4ZVw13rpXiWijFs3dZ3M"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

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
    import os

# Usa el puerto que Render asigna automáticamente
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port, debug=True)
