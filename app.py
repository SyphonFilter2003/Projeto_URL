from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import firebase_admin
import firebase_admin.auth as auth
from google.cloud.firestore_v1 import FieldFilter
from firebase_admin import credentials, firestore

# Inicializa o Flask
app = Flask(__name__)
app.secret_key = "sua_chave_secreta_aqui"  # Troque por uma chave segura!

# Configura o Firebase
cred = credentials.Certificate("firebase-creds.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Teste de conexão
try:
    users_ref = db.collection("users")
    print("✅ Firebase conectado com sucesso!")
except Exception as e:
    print(f"❌ Erro no Firebase: {e}")

# Rota da página inicial
@app.route("/")
def home():
    if "user" in session:
        return render_template("home.html", user=session["user"])
    return redirect(url_for("login"))

# Rota de login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        try:
            # Verifica se o usuário existe (isso NÃO faz login, apenas busca)
            user = auth.get_user_by_email(email)
            
            session["user"] = email
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for("home"))
        except auth.UserNotFoundError:
            flash("E-mail não cadastrado.", "danger")
        except Exception as e:
            flash("Erro ao fazer login.", "danger")
            print(f"Erro: {e}")

    return render_template("login.html")

# Rota de registro
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        password_confirm = request.form.get("password_confirm", "")

        # Validações
        if not email or "@" not in email:
            flash("E-mail inválido.", "danger")
        elif password != password_confirm:
            flash("Senhas não coincidem.", "danger")
        elif len(password) < 6:
            flash("Senha muito curta (mínimo 6 caracteres).", "danger")
        else:
            try:
                # Cria usuário no Firebase Auth
                user = auth.create_user(email=email, password=password)
                flash("Conta criada com sucesso! Faça login.", "success")
                return redirect(url_for("login"))
            except auth.EmailAlreadyExistsError:
                flash("E-mail já cadastrado.", "danger")
            except Exception as e:
                flash("Erro ao criar conta.", "danger")
                print(f"Erro: {e}")

    return render_template("register.html")

# Rota de logout
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)