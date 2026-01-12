import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from auth import iniciar_oauth, finalizar_oauth
from werkzeug.middleware.proxy_fix import ProxyFix
import drive
from datetime import datetime

app = Flask(__name__, template_folder="templates", static_folder="static")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.config["PREFERRED_URL_SCHEME"] = "https"


@app.route("/")
def index():
    if "credentials" not in session:
        return redirect(url_for("login"))

    processos = drive.listar_processos()
    # adiciona arquivos a cada processo
    for p in processos:
        p["arquivos"] = drive.listar_arquivos(p["id"])
    return render_template("index.html", processos=processos, drive=drive)


@app.route("/login")
def login():
    return iniciar_oauth()


@app.route("/oauth2callback")
def oauth_callback():
    return finalizar_oauth()


@app.route("/criar", methods=["POST"])
def criar():
    descricao = request.form["descricao"].strip()
    nome_pasta = f"{datetime.now():%Y%m%d_%H%M%S}_{descricao.replace(' ', '_')}"
    drive.criar_pasta(nome_pasta)
    flash("✅ Processo criado com sucesso!", "success")
    return redirect(url_for("index"))


@app.route("/upload/<pasta_id>", methods=["POST"])
def upload(pasta_id):
    arquivos = request.files.getlist("files")
    for f in arquivos:
        drive.upload_arquivo(pasta_id, f)
    flash("📤 Arquivo(s) anexado(s) com sucesso.", "success")
    return redirect(url_for("index"))


@app.route("/excluir/<file_id>")
def excluir(file_id):
    drive.excluir_arquivo(file_id)
    flash("🗑️ Arquivo excluído.", "warning")
    return redirect(url_for("index"))


@app.route("/editar/<pasta_id>", methods=["POST"])
def editar_processo(pasta_id):
    nova_descricao = request.form["novo_nome"].strip()
    nome_atual = drive.obter_nome_pasta(pasta_id)
    prefixo = nome_atual.split("_", 1)[0]
    novo_nome = f"{prefixo}_{nova_descricao.replace(' ', '_')}"
    drive.renomear_pasta(pasta_id, novo_nome)
    flash("✏️ Nome do processo atualizado!", "info")
    return redirect(url_for("index"))


@app.route("/excluir_todos/<pasta_id>")
def excluir_todos(pasta_id):
    arquivos = drive.listar_arquivos(pasta_id)
    for a in arquivos:
        drive.excluir_arquivo(a["id"])
    flash("🗑️ Todos os arquivos do processo foram excluídos.", "warning")
    return redirect(url_for("index"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
