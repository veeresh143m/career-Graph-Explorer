import os
from flask import Flask, render_template, request, redirect, url_for, g
from db import CognoDBClient, QueryError
app = Flask(__name__)

def get_client():
    if "db_client" not in g:
        g.db_client = CognoDBClient()
    return g.db_client

@app.teardown_appcontext
def shutdown_db(exception=None):
    client = g.pop("db_client", None)
    if client:
        client.close()

@app.route("/")
def index():
    try:
        client = get_client()
        roles = client.list_roles()
        skills = client.list_skills()
        return render_template("index.html", roles=roles, skills=skills)
    except QueryError as error:
        return render_template("error.html", error=str(error)), 500

@app.route("/role/<path:name>")
def role_detail(name):
    try:
        client = get_client()
        item = client.get_role_details(name)
        if not item:
            return render_template("error.html", error=f"Role '{name}' not found."), 404
        return render_template("detail.html", title=item["name"], subtitle="Role details", description=item["description"], details=item)
    except QueryError as error:
        return render_template("error.html", error=str(error)), 500

@app.route("/skill/<path:name>")
def skill_detail(name):
    try:
        client = get_client()
        item = client.get_skill_details(name)
        if not item:
            return render_template("error.html", error=f"Skill '{name}' not found."), 404
        return render_template("detail.html", title=item["name"], subtitle="Skill details", description=item["description"], details=item)
    except QueryError as error:
        return render_template("error.html", error=str(error)), 500

@app.route("/course/<path:name>")
def course_detail(name):
    try:
        client = get_client()
        item = client.get_course_details(name)
        if not item:
            return render_template("error.html", error=f"Course '{name}' not found."), 404
        return render_template("detail.html", title=item["name"], subtitle=f"Course by {item['provider']}", description=item["description"], details=item)
    except QueryError as error:
        return render_template("error.html", error=str(error)), 500

@app.route("/search")
def search():
    query = request.args.get("q", "").strip()
    if not query:
        return redirect(url_for("index"))
    try:
        client = get_client()
        results = client.search_nodes(query)
        return render_template("search.html", query=query, results=results)
    except QueryError as error:
        return render_template("error.html", error=str(error)), 500

if __name__ == "__main__":
    host = os.getenv("FLASK_RUN_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_RUN_PORT", 5000))
    app.run(host=host, port=port, debug=True)
