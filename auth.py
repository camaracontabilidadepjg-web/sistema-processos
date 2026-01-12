from flask import session, redirect, url_for, request, flash
from google_auth_oauthlib.flow import Flow
import os

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CLIENT_SECRET_FILE = os.environ.get(
    "GOOGLE_CLIENT_SECRET_FILE",
    os.path.join(BASE_DIR, "client_secret.json")
)


def iniciar_oauth():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES,
        redirect_uri=url_for("oauth_callback", _external=True)
    )

    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"
    )

    session["state"] = state
    return redirect(auth_url)


def finalizar_oauth():
    if "state" not in session:
        flash("⚠️ Estado da autenticação não encontrado. Tente novamente.", "danger")
        return redirect(url_for("login"))

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES,
        state=session["state"],
        redirect_uri=url_for("oauth_callback", _external=True)
    )

    flow.fetch_token(authorization_response=request.url)

    creds = flow.credentials

    session["credentials"] = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes
    }

    flash("✅ Autenticação realizada com sucesso!", "success")
    return redirect(url_for("index"))
