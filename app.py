from flask import Flask, render_template, request, redirect, session
from db import engine, Base, SessionLocal
from ai import analyze_resume
import models
import PyPDF2
import docx
import json
from ai import analyze_resume

app= Flask(__name__)
app.secret_key= "secret123"

Base.metadata.create_all(bind=engine)

#Home
@app.route("/")
def home():
    if "user" in session:
        return redirect("/dashboard")
    return redirect("/login")

@app.route("/signup", methods=["GET", "POST"])
def signUp():
    db = SessionLocal()

    try:
        if request.method == "POST":
            email = request.form.get("email").strip()
            password = request.form.get("password").strip()

            existing_user = db.query(models.User).filter_by(email=email).first()
            if existing_user:
                return "User already exists"

            user = models.User(email=email, password=password)
            db.add(user)
            db.commit()

            return redirect("/login")

        return render_template("signup.html")

    finally:
        db.close()
#Login
@app.route("/login", methods=["GET", "POST"])
def login():
    db = SessionLocal()

    try:
        if request.method == "POST":
            email = request.form.get("email").strip()
            password = request.form.get("password").strip()

            user = db.query(models.User).filter_by(email=email).first()

            if user and user.password == password:
                session["user"] = user.email
                return redirect("/dashboard")
            else:
                return "Invalid credentials"

        return render_template("login.html")

    finally:
        db.close()
#Dashboard
@app.route("/dashboard",methods=["GET","POST"])
def dashboard():
    if "user" not in session:
        return redirect("/login")
    
    result=None

    if request.method=="POST":
        user_goal= request.form.get("role")
        resume_text= request.form.get("resume")

        file= request.files.get("file")

        #file handling
        if file and file.filename !="":
            if file.filename.endswith(".pdf"):
                try:
                    pdf_reader= PyPDF2.PdfReader(file)
                    text=""
                    for page in pdf_reader.pages:
                        text+= page.extract_text() or ""
                    resume_text= text
                except Exception as e:
                    result= {"error": f"PDF error: {str(e)}"}
            elif file.filename.endswith(".docx"):
                try:
                    doc = docx.Document(file)
                    text=""
                    for para in doc.paragraphs:
                        text+= para.text+"\n"
                    resume_text=text
                except Exception as e:
                    result= {"error": f"Dodx error: {str(e)}"}

        #AI call
        if resume_text and user_goal:
            try:
                result= analyze_resume(resume_text,user_goal)
                #Stop if ai returned error
                if "error" in result:
                    return render_template(
                        "dashboard.html",
                        user=session["user"],
                        result=result
                        ) 
                #save to db
                db= SessionLocal()
                user= db.query(models.User).filter_by(email=session["user"]).first()
                
                report= models.Report(

                    user_id=user.id,
                    resume_text=resume_text,
                    result= json.dumps(result)
                )
                db.add(report)
                db.commit()

            except Exception as e:
                result= {"error":f"AI error: {str(e)}"}

    return render_template("dashboard.html",user=session["user"],result=result)

#history
@app.route("/history")
def history():
    if "user" not in session:
        return redirect("/login")

    db = SessionLocal()
    user = db.query(models.User).filter_by(email=session["user"]).first()

    reports = db.query(models.Report).filter_by(user_id=user.id).all()

    passed_reports = []

    for r in reports:
        try:
            parsed_result = json.loads(r.result)  
        except:
            parsed_result = {
                "skills": [],
                "missing_skills": [],
                "roadmap": [],
                "interview_questions": [],
                "career_prospects": []
            }

        passed_reports.append({
            "resume": r.resume_text,
            "result": parsed_result
        })

    return render_template("history.html", reports=passed_reports)
#logout
@app.route("/logout")
def logout():
    session.pop("user",None)
    return redirect("/login")
print(models.Report.__table__.columns.keys())

if __name__=="__main__":
    
    app.run(debug=True)