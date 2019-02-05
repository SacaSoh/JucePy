from functools import wraps
from multiprocessing import Process

import requests
from cs50 import SQL
from flask import redirect, session

from scrappers.scrapper_CE import ce_update

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///jucepy.db")


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def protocol_update(protocol, protocol_uf):
    """Retrieve data from active processes at Trade Board and update at database
       Takes protocol number and State ("uf") as input"""

    if protocol_uf == 'CE':
        # contact Ceará Trade Board to retrieve process info
        try:
            return ce_update(protocol)
        except requests.RequestException:
            return None
    else:
        return None


# Update all active processes - set up the db update process in another thread, so as to avoid blocking the
# execution of Flask
class ThreadedUpdate:

    def __init__(self):
        p = Process(target=self.run, args=())
        p.daemon = True                       # Daemonize it
        p.start()                             # Start the execution

    def run(self):

        activeprocessinfo = db.execute("SELECT * FROM processos WHERE ativo = 1 ORDER BY timestamp DESC")

        # get each process basic current info
        for processo in activeprocessinfo:
            # info used to update the process
            protocol = processo.get('protocol')
            protocol_uf = processo.get('uf')

            # info used to check if there's an updates situation or same as last
            oldsituacao = processo.get('status')
            oldpendencias = processo.get('msgjucec')
            olddataretorno = processo.get('dataretorno')

            # new info for comparison
            updatedinfo = protocol_update(protocol, protocol_uf)

            try:
                newsituacao = updatedinfo.get('situacao')
                newpendencias = updatedinfo.get('pendencias')
                newdataretorno = updatedinfo.get('dataretorno')
            except:
                return None

            # if there's new info, update at processos table and log at historico table
            if (oldsituacao != newsituacao) or (oldpendencias != newpendencias) or (olddataretorno != newdataretorno):
                # update process info
                db.execute("UPDATE processos SET timestamp=datetime('now'),status=:status, nomeemp=:nomeemp, \
                            cnpj=:cnpj, nire=:nire, dataentrada=:dataentrada, dataretorno=:dataretorno, \
                            msgjucec=:pendencias, dataaprovacao=:dataaprovacao WHERE protocol=:protocol AND uf=:uf",
                            status=updatedinfo['situacao'], nomeemp=updatedinfo['nome'], cnpj=updatedinfo['cnpj'],
                            nire=updatedinfo['nire'], dataentrada=updatedinfo['dataentrada'],
                            dataretorno=updatedinfo['dataretorno'],pendencias=updatedinfo['pendencias'],
                            dataaprovacao=updatedinfo['dataaprovacao'], protocol=protocol, uf=protocol_uf)

                # log update operation at history table
                db.execute("INSERT INTO historico (protocol, status, msgjucec, uf, dataretorno) VALUES (:protocol, \
                          :status, :msgjucec, :uf, :dataretorno)", protocol=protocol, status=updatedinfo['situacao'],
                          msgjucec=updatedinfo['pendencias'], uf=protocol_uf, dataretorno=updatedinfo['dataretorno'])


# update a single process (to be used when process is added to the system)
class ThreadedSingleUpdate:

    def __init__(self, protocol, protocol_uf):
        self.protocol = protocol
        self.protocolUF = protocol_uf
        p = Process(target=self.run, args=())
        p.daemon = True                       # Daemonize it
        p.start()                             # Start the execution

    def run(self):

            # new info for comparison
            updatedinfo = protocol_update(self.protocol, self.protocolUF)

            try:
                newsituacao = updatedinfo.get('situacao')
                newpendencias = updatedinfo.get('pendencias')
                newdataretorno = updatedinfo.get('dataretorno')
            except:
                return None


            db.execute("UPDATE processos SET timestamp=datetime('now'), status=:status, nomeemp=:nomeemp, \
                        cnpj=:cnpj, nire=:nire, dataentrada=:dataentrada, dataretorno=:dataretorno, \
                        msgjucec=:pendencias, dataaprovacao=:dataaprovacao WHERE protocol=:protocol AND uf=:uf",
                        status=updatedinfo['situacao'], nomeemp=updatedinfo['nome'], cnpj=updatedinfo['cnpj'],
                        nire=updatedinfo['nire'], dataentrada=updatedinfo['dataentrada'],
                        dataretorno=updatedinfo['dataretorno'], pendencias=updatedinfo['pendencias'],
                        dataaprovacao=updatedinfo['dataaprovacao'], protocol=self.protocol, uf=self.protocolUF)

            # log update operation at history table
            db.execute("INSERT INTO historico (protocol, status, msgjucec, uf, dataretorno) VALUES (:protocol, \
                      :status, :msgjucec, :uf, :dataretorno)", protocol=self.protocol, status=updatedinfo['situacao'],
                      msgjucec=updatedinfo['pendencias'], uf=self.protocolUF, dataretorno=updatedinfo['dataretorno'])