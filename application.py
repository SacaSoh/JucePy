import re
import sys
import threading
from tempfile import mkdtemp

# deal with werkzeug deprecation warnings as of version 0.15
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

# deprecation warning - import have to be done here to avoid the warning on indirect import
from werkzeug.contrib.cache import FileSystemCache

from helpers import login_required, ThreadedUpdate, ThreadedSingleUpdate


"""
update active Trade Board processes after a set time - it uses threading to avoid the halting of listening 
functions 
"""
def process_update_call():


    try:
        ThreadedUpdate()
        threading.Timer(3600, process_update_call).start()
    except:
        print(f'Process update call failed', file=sys.stderr)


# function for single update - to be used when a protocol is added
def single_process_update_call(protocol, protocolUF):
    try:
        ThreadedSingleUpdate(protocol, protocolUF)
    except:
        print(f'Process update call failed', file=sys.stderr)


# Configure application
app = Flask(__name__)
app.config['DEBUG'] = False


# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///jucepy.db")

# call process_update_call at app initialization to setup timer
threading.Timer(15, process_update_call).start()
print(f'process_update_call initialization', file=sys.stderr)


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Show active trade board cases"""

    # send basic html on access, to be completed by info thru POST request as below, and JS at client
    if request.method == "GET":

        return render_template("index.html")

    # POST request for JSON object
    else:
        activeprocessinfo = db.execute("SELECT timestamp, protocol, uf, nomeemp, descricao, status, dataaprovacao, \
                                       msgjucec, nire, cnpj, respadd, respbaixa, dataentrada FROM processos WHERE  \
                                       ativo = 1 ORDER BY timestamp DESC")

        return jsonify(data=activeprocessinfo)


@app.route("/inativos", methods=["GET", "POST"])
@login_required
def inativos():
    """Show inactive trade board cases"""

    # send basic html on access, to be completed by info thru POST request as below, and JS at client
    if request.method == "GET":

        return render_template("inativos.html")

    else:
        # get list of active processes
        inactiveprocessinfo = db.execute("SELECT timestamp, protocol, uf, nomeemp, descricao, status, dataaprovacao, \
                                         msgjucec, nire, cnpj, respadd, respbaixa, dataentrada FROM processos WHERE \
                                         ativo = 0 ORDER BY timestamp DESC")

        if inactiveprocessinfo == None:
            inactiveprocessinfo = ''

        return jsonify(data=inactiveprocessinfo)


@app.route("/adicionar", methods=["GET", "POST"])
@login_required
def adicionar():
    """Add a process to tracker"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # get protocolno in numeric form
        protocol = str(re.sub("[^0-9]", "", request.form.get("protocolno")))
        descricao = request.form.get("descricao")
        uf = request.form.get("uf")
        print(f'{protocol}, {descricao}, {uf}', file=sys.stderr)

        # ensure protocol subsmited is composed of 9 digits:
        if len(protocol) != 9:
            flash('Número Inválido!')
            return redirect("/adicionar")

        # update database - check if protocol is already on the database
        protocol_info = db.execute("SELECT * FROM processos WHERE protocol =:protocol AND ativo = 1 AND uf =:uf",
                                   protocol=protocol, uf=uf)

        print(f'{protocol_info}', file=sys.stderr)

        # protocol already in DB, alert user
        if protocol_info and (protocol in protocol_info[0].values() and uf in protocol_info[0].values()):
            error = f'Protocolo {protocol} - {uf} já consta do sistema!'
            print(f'duplicated protocol no', file=sys.stderr)
            return render_template("adicionar.html", error=error)

        # protocol not in DB, insert as new row
        else:
            userinfo = db.execute("SELECT * FROM users WHERE id = :userid", userid=session["user_id"])[0]['username']

            db.execute("INSERT INTO processos (protocol, uf, respadd, descricao) VALUES (:protocol, :uf, :respadd, \
                       :descricao)", protocol=protocol, uf=uf, respadd=userinfo, descricao=descricao)

            # also insert in process history as entry 0
            db.execute("INSERT INTO historico (indexevento, protocol, uf, status) VALUES (:indexevento, :protocol, :uf,\
                        :status)", indexevento=0, protocol=protocol, uf=uf, status='Protocolo adicionado ao sistema')

            # update protocol status
            single_process_update_call(protocol, uf)

            # flash sucess
            flash(f'Processo nº {protocol} inserido no sistema com sucesso - aguarde atualização do status.')
            return redirect("/adicionar")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("adicionar.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            error = 'Necessário informar nome de usuário'
            print(f'username not informed error', file=sys.stderr)
            return render_template("login.html", error=error)

        # Ensure password was submitted
        elif not request.form.get("password"):
            error = 'Necessário informar password'
            print(f'password not informed error', file=sys.stderr)
            return render_template("login.html", error=error)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            error = 'Usuário ou Password Inválido(s)'
            print(f'invalid user/password error', file=sys.stderr)
            return render_template("login.html", error=error)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page and flash sucess
        user = request.form.get("username")
        flash(f'Usuário {user} logado com sucesso!')
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        error = None

        # Ensure username was submitted
        if len(request.form.get("username")) < 5:
            error = 'Necessário informar nome de usuário com ao menos 5 caracteres'
            print(f'username lenght error', file=sys.stderr)
            return render_template("register.html", error=error)

        # Ensure username is unique
        elif len(db.execute("SELECT * FROM users WHERE username =:username",
                            username=request.form.get("username"))) != 0:
            error = 'Nome de usuário já existe!'
            print(f'duplicated username', file=sys.stderr)
            return render_template("register.html", error=error)

        # Ensure password was submitted
        elif 8 < len(request.form.get("password")) > 16:
            error = 'Password deve ter entre 8 e 16 caracteres alfanuméricos'
            print(f'password outside bounds', file=sys.stderr)
            return render_template("register.html", error=error)

        # Check if both password fields match
        elif request.form.get("confirmation") != request.form.get("password"):
            error = 'Password e confirmação não batem.'
            print(f'password confirmation failed', file=sys.stderr)
            return render_template("register.html", error=error)

        else:
            # If everything above is fine, register user at database
            db.execute("INSERT INTO users (username, hash) VALUES (:username, :pass_hash)",
                      username=request.form.get("username"),
                      pass_hash=generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8))

        # get user id and log the registered user
            rows = db.execute("SELECT * FROM users WHERE username =:username",
                              username=request.form.get("username"))
            session["user_id"] = rows[0]["id"]

        # flash sucess
            user = request.form.get("username")
            flash(f'Usuário {user} registrado com sucesso!')

        # Redirect user to home page
            return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/historico", methods=["GET", "POST"])
@login_required
def historico():
    """Show history of a specific case - send JSON to be processed by JS"""

    if request.method == "POST":

        clickedprotocol = request.json["data"]

        historicoinfo = db.execute("SELECT * FROM historico WHERE protocol=:protocol ORDER BY dataevento DESC",
                                  protocol=clickedprotocol)

        return jsonify(historicoinfo)

    else:
        return redirect("/")


@app.route("/finalizar", methods=["GET", "POST"])
@login_required
def finalizar():
    """closes a specific process - i.e. set "Ativo" to 0"""

    if request.method == "POST":

        protocoloencerrado = request.json["data"]

        # get user id
        username = db.execute("SELECT username FROM users WHERE id=:userid", userid=session["user_id"])[0]['username']

        # update process status and set respbaixa (responsible for the event)
        db.execute("UPDATE processos SET ativo = 0, respbaixa=:user WHERE protocol=:protocol",
                   protocol=protocoloencerrado, user=username)

        # trigger ajax sucess
        return '200'

    else:
        return redirect("/")

@app.route("/update")
@login_required
def update():
    """DEBUG - force update of processes"""

    # call function
    ThreadedUpdate()
    print(f'process_update_call manually ran by user "/update"', file=sys.stderr)
    return redirect("/")

def errorhandler(e):
    """Handle error"""
    if e.name:
        print(f'{e.name}, {e.code}', file=sys.stderr)
    else:
        print(f'{e.code}', file=sys.stderr)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)


if __name__ == "__main__":
    app.run(host='0.0.0.0', threaded=True)
