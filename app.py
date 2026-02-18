from flask import Flask,render_template,request,redirect,session
from search_engine.search import ranked_search
from math_engine.solver import solve_math_query
from ai_engine.mistral_client import ask_mistral
from database.db import init_db
from werkzeug.security import generate_password_hash, check_password_hash
from flask import jsonify
import sqlite3

#STARTING POINT OF CODE
app=Flask(__name__)
app.secret_key="supersecretkey"

init_db()       #initialize databse for login and signup

#SIGN UP ROUTE
@app.route("/signup",methods=["GET","POST"])
def signup():
    if request.method=="POST":
        username=request.form["username"]
        password=request.form["password"]
        hashed_password=generate_password_hash(password)
        try:
            conn=sqlite3.connect("database.db")
            cursor=conn.cursor()
            cursor.execute("INSERT INTO users (username,password) VALUES (?,?)",(username,hashed_password))
            
            conn.commit()
            conn.close()
            return redirect("/login")
        except sqlite3.IntegrityError:
            return "Username already exists"
        
    return render_template("signup.html") 

#LOGIN ROUTE
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT password FROM users WHERE username = ?", (username,)
        )
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[0], password):
            session["user"] = username
            session["mode"] = "offline"  # DEFAULT MODE
            return redirect("/")
        else:
            return "Invalid username or password"

    return render_template("login.html")
                
#LOGOUT
@app.route("/logout")
def logout():
    session.pop("user",None)
    return redirect("/login")

#ONLINE OFFLINE TOGGLE
@app.route("/toggle_mode", methods=["POST"])
def toggle_mode():
    if "user" not in session:
        return redirect("/login")

    current = session.get("mode", "offline")
    session["mode"] = "online" if current == "offline" else "offline"

    return redirect(request.referrer or "/")
 

#app route/HOME PAGE
@app.route("/")
def index():
    if "user" not in session:
        return redirect("/login")
    return render_template("index.html",query="")

#SEARCH 
@app.route("/search",methods=["GET","POST"])       #/search route reads ?query=... from URL
def search():
    if "user" not in session:
        return redirect("/login")
    if request.method=="GET":
        return redirect("/")
    
    query=request.form.get("query","").strip()       #request is an object that represents the current HTTP request, request.args contains the query parameters sent in the URL, .get("query", "") tries to fetch the value associated with the key "query", If "query" is not present in the request, an empty string ("") is returned
    mode=session.get("mode","offline")
    
    # STORE SEARCH HISTORY (LAST 10)
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO search_history (username, query) VALUES (?, ?)",
        (session["user"], query),
    )

    cursor.execute(
        """DELETE FROM search_history WHERE id NOT IN (SELECT id FROM search_history WHERE username = ? ORDER BY created_at DESC LIMIT 10 ) AND username = ?""",
        (session["user"], session["user"]),
    )

    conn.commit()
    conn.close()
    
    if mode == "offline":
        # Math engine
        math_keywords = ["differentiate","derivative","integrate","solve","limit","sin","cos","tan","log"]
        is_math_intent = any(k in query.lower() for k in math_keywords)

        if is_math_intent:
            math_result = solve_math_query(query)
            return render_template(
                "results.html",
                query=query,
                math_result=math_result,
                results=[],
                ai_answer=None
            )

        # Ranked search
        results = ranked_search(query)
        return render_template(
            "results.html",
            query=query,
            math_result=None,
            results=results,
            ai_answer=None,
            mode=mode
        )


    # AI SEARCH (ONLINE MODE ONLY)
    ai_answer = ask_mistral(f"Answer briefly and clearly: {query}")
    return render_template(
        "results.html",
         query=query,
         math_result=None,
         results=None,
         ai_answer=ai_answer,
         mode=mode,
        )
    
#HISTORY
@app.route("/history")
def history():
    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, query, created_at FROM search_history WHERE username=? ORDER BY created_at DESC",
        (session["user"],)
    )

    history = cursor.fetchall()
    conn.close()

    return render_template("history.html", history=history)


#DELETE HISTORY
@app.route("/delete_history/<int:history_id>", methods=["POST"])
def delete_history(history_id):
    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM search_history
        WHERE id = ? AND username = ?
    """, (history_id, session["user"]))

    conn.commit()
    conn.close()

    return redirect("/history")

#VOICE ASSISSTANT
@app.route("/voice_ai", methods=["POST"])
def voice_ai():
    if "user" not in session:
        return jsonify({"answer": "Please log in first."})

    if session.get("mode", "offline") != "online":
        return jsonify({"answer": "Voice assistant is available only in online mode."})

    data = request.get_json()
    query = data.get("query", "").strip()

    if not query:
        return jsonify({"answer": "I didn't catch that."})

    answer = ask_mistral(f"Answer briefly and clearly: {query}")
    return jsonify({"answer": answer})

#RUN LINE
if __name__=="__main__":
    app.run(debug=True)