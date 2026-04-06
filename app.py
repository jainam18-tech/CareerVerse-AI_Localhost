import os
import uuid
import base64
import json
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory, flash
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail, Message
from datetime import datetime
from openai import OpenAI
from PIL import Image
from config import Config
from ocr.preprocess import preprocess_image
from ocr.ocr_engine import extract_text
from report_generator import generate_pdf_report
from models import db, User, LoginHistory, ChatHistory, UserPerformance
from sqlalchemy.engine.url import make_url
import pymysql

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
mail = Mail(app)

def generate_verification_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])

def confirm_verification_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False
    return email

def send_verification_email(to, username, token):
    verification_url = url_for('verify_email', token=token, _external=True)
    html = render_template('email/verify_email.html', username=username, verification_url=verification_url)
    subject = "Verify your CareerVerse Account"
    
    # Debug log
    print("\n" + "!" * 50)
    print(f"DEBUG: Attempting to send verification email to {to}")
    print(f"DEBUG: Verification link: {verification_url}")
    print("!" * 50 + "\n")
    
    if not app.config.get('MAIL_USERNAME') or app.config.get('MAIL_USERNAME') == 'your-email@gmail.com':
        print("\n" + "*" * 50)
        print("WARNING: SMTP credentials not configured. Skipping real email sending.")
        print(f"MOCK EMAIL: To: {to}\nSubject: {subject}\nVerification URL: {verification_url}")
        print("*" * 50 + "\n")
        return True

    try:
        msg = Message(subject, recipients=[to], html=html)
        mail.send(msg)
        print(f"DEBUG: Email sent successfully to {to}")
    except Exception as e:
        print(f"ERROR: Failed to send email via SMTP: {e}")
        print(f"MOCK EMAIL FALLBACK: Verification URL for {to}: {verification_url}")
        # We don't raise here, just log it. Signup should still proceed.
    return True


os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

client = OpenAI(api_key=app.config["OPENAI_API_KEY"])


# Mock User Database (Temporary)
USERS = {
    "test@example.com": {
        "username": "Test User",
        "password": "password123"
    }
}



# Load Career Knowledge Base
KNOWLEDGE_PATH = os.path.join(os.path.dirname(__file__), "career_knowledge.json")
with open(KNOWLEDGE_PATH, "r") as f:
    CAREER_KNOWLEDGE = json.load(f)


# ─────────────────────────── HELPERS ───────────────────────────

def get_settings():
    """Return current session settings, falling back to defaults."""
    defaults = Config.DEFAULT_SETTINGS.copy()
    for key, val in defaults.items():
        if key not in session:
            session[key] = val
    return {k: session[k] for k in defaults}


@app.context_processor
def inject_history():
    """Make user's analysis history available globally for sidebars."""
    if session.get("logged_in") and session.get("user_id"):
        # Get last 10 non-hidden analyses for sidebar
        history = UserPerformance.query.filter_by(
            user_id=session["user_id"], 
            is_hidden=False
        ).order_by(UserPerformance.created_at.desc()).limit(10).all()
        return dict(user_history=history)
    return dict(user_history=[])


def extract_first_name(full_name):
    if not full_name:
        return "User"
    name_parts = full_name.strip().split()
    name_parts = [p for p in name_parts if len(p) > 1]
    if len(name_parts) == 1:
        return name_parts[0].capitalize()
    father_suffixes = ["bhai", "kumar", "lal", "das", "singh"]
    for i in range(len(name_parts) - 1, -1, -1):
        part = name_parts[i]
        if any(part.lower().endswith(suffix) for suffix in father_suffixes):
            if i > 0:
                return name_parts[i - 1].capitalize()
    if len(name_parts) >= 2:
        return name_parts[1].capitalize()
    return name_parts[0].capitalize()


def analyze_strength_weakness(marks):
    """Perform a statistical analysis to predict strengths and weaknesses."""
    if not marks:
        return {"strengths": [], "weaknesses": [], "traits": []}
    
    values = list(marks.values())
    avg = sum(values) / len(values) if values else 0
    
    # Clusters mapping
    clusters = {
        "Quantitative": ["Mathematics", "Maths", "Physics", "Statistics"],
        "Verbal": ["English", "Gujarati", "Hindi", "Sanskrit"],
        "Scientific": ["Science", "Biology", "Chemistry"],
        "Business": ["Account", "Economics", "Org. of Comm", "Elements of Accounts", "Business", "Statistics"]
    }
    
    strengths = []
    weaknesses = []
    traits = []
    
    # Identify deltas
    for subject, mark in marks.items():
        if mark > avg * 1.15 or mark >= 90:
            strengths.append(subject)
        elif mark < avg * 0.85 or mark <= 35:
            weaknesses.append(subject)
            
    # Trait Prediction (Clustering)
    active_clusters = {name: [] for name in clusters}
    for sub, mark in marks.items():
        for cluster_name, sub_list in clusters.items():
            if any(s.lower() in sub.lower() for s in sub_list):
                active_clusters[cluster_name].append(mark)
                
    for name, cluster_marks in active_clusters.items():
        if cluster_marks:
            cluster_avg = sum(cluster_marks) / len(cluster_marks)
            if cluster_avg > 80:
                if name == "Quantitative": traits.append("Analytical & Logical")
                if name == "Verbal": traits.append("Rhetorical & Expressive")
                if name == "Scientific": traits.append("Investigative & Empirical")
                if name == "Business": traits.append("Managerial & Commercial")

    return {
        "strengths": strengths,
        "weaknesses": weaknesses,
        "traits": traits,
        "average": round(avg, 2)
    }


def detect_academic_level(subject_list):
    subjects = [s.upper() for s in subject_list]
    if "MATHEMATICS" in subjects and "SCIENCE" in subjects and "SOCIAL SCIENCE" in subjects:
        return "SSC Academic Performance"
    if "PHYSICS" in subjects and "CHEMISTRY" in subjects and "MATHEMATICS" in subjects:
        return "HSC Science A Academic Performance"
    if "PHYSICS" in subjects and "CHEMISTRY" in subjects and "BIOLOGY" in subjects:
        return "HSC Science B Academic Performance"
    commerce_subjects = ["ACCOUNT", "ECONOMICS", "STATISTICS", "ORG. OF COMM", "ELEMENTS OF ACC", "BUSINESS"]
    if any(com in subject for subject in subjects for com in commerce_subjects):
        return "HSC Commerce Academic Performance"
    return "Academic Performance"


def speak_openai(text):
    try:
        temp_dir = "temp_voices"
        os.makedirs(temp_dir, exist_ok=True)
        file_path = os.path.join(temp_dir, f"{uuid.uuid4()}.mp3")
        voice = session.get("voice_type", "nova")
        response = client.audio.speech.create(
            model="tts-1",  # Use tts-1 for faster response if needed, or stick to gpt-4o-mini-tts if intended
            voice=voice,
            input=text,
        )
        response.stream_to_file(file_path)
        return file_path
    except Exception as e:
        print("TTS Error:", e)
        return None


# ─────────────────────────── ROUTES ───────────────────────────

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static', 'images'),
                               'favicon_v5_final.png', mimetype='image/png')

@app.route("/")
def welcome():
    return render_template("welcome.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            email = request.form.get("email")
            password = request.form.get("password")
            
            user = User.query.filter_by(email=email).first()
            print(f"DEBUG: Login attempt for {email}. User found: {user is not None}")
            if user and check_password_hash(user.password_hash, password):
                print(f"DEBUG: Password correct for {email}. is_verified: {user.is_verified}")
                if not user.is_verified:
                    return render_template("login.html", error="Please verify your email address before logging in. Check your inbox!")
                
                session["logged_in"] = True
                session["user_name"] = user.username
                session["user_email"] = email
                session["is_admin"] = user.is_admin
                session["user_id"] = user.id
                
                # Log login history
                new_login = LoginHistory(user_id=user.id)
                db.session.add(new_login)
                
                # ── Restore session from latest performance ──
                latest_perf = UserPerformance.query.filter_by(user_id=user.id, is_hidden=False).order_by(UserPerformance.created_at.desc()).first()
                if latest_perf:
                    session["marks"] = json.loads(latest_perf.marks_json)
                    session["performance"] = latest_perf.performance_level
                    session["analyzed_name"] = latest_perf.analyzed_name
                    session["current_perf_id"] = latest_perf.id
                    session["marks_ready"] = True
                else:
                    session["marks_ready"] = False
                    
                db.session.commit()
                return redirect(url_for("home"))
            else:
                return render_template("login.html", error="Invalid email or password")
        except Exception as e:
            print(f"DEBUG: Error in login: {e}")
            return render_template("login.html", error=f"Login error: {str(e)}")
            
    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        try:
            username = request.form.get("username")
            email = request.form.get("email")
            password = request.form.get("password")
            
            # Simple validation
            if not username or not email or not password:
                return jsonify({"error": "Missing required fields"})

            print(f"DEBUG: Processing signup for {email}")
            
            if User.query.filter_by(email=email).first():
                return jsonify({"error": "Email already registered. Please login."})
                
            new_user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password),
                is_verified=False
            )
            db.session.add(new_user)
            db.session.commit()
            print(f"DEBUG: User {email} created in database.")
            
            # Send verification email
            token = generate_verification_token(email)
            try:
                # Using a separate try-except for email so signup doesn't fail if SMTP fails
                send_verification_email(email, username, token)
            except Exception as e:
                print(f"DEBUG: Error sending email: {e}")
            
            return jsonify({"success": True, "message": "Account created, check your email and verify to login"})
            
        except Exception as e:
            print(f"DEBUG ERROR in signup flow: {str(e)}")
            db.session.rollback()
            return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500
            
    return render_template("signup.html")


@app.route("/verify/<token>")
def verify_email(token):
    email = confirm_verification_token(token)
    if not email:
        flash("The verification link is invalid or has expired.", "danger")
        return redirect(url_for("login"))
    
    user = User.query.filter_by(email=email).first_or_404()
    if user.is_verified:
        flash("Account already verified. Please login.", "info")
    else:
        user.is_verified = True
        db.session.commit()
        flash("You have confirmed your account. Thanks!", "success")
    
    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("welcome"))


@app.route("/home")
def home():
    if not session.get("logged_in"):
        return redirect(url_for("welcome"))
    
    if session.get("marks_ready"):
        return redirect(url_for("results"))
        
    settings = get_settings()
    return render_template("home.html", settings=settings)


@app.route("/upload", methods=["POST"])
def upload():
    """Handle OCR marksheet upload."""
    file = request.files.get("marksheet")
    if not file or file.filename == "":
        return redirect(url_for("home"))

    os.makedirs("data", exist_ok=True)
    path = os.path.join("data", file.filename)
    file.save(path)

    img = Image.open(path)
    processed_img = preprocess_image(img)
    name, subjects = extract_text(processed_img)

    if subjects:
        session["analyzed_name"] = name.strip() if name else "Student"
        session["marks"] = subjects
        session["marks_ready"] = True
        session["performance"] = detect_academic_level(list(subjects.keys()))
        session["welcome_spoken"] = False
        # Only eligible for welcome speech if voice is already ON when uploading
        session["welcome_eligible"] = get_settings().get("voice_enabled", False)
        
        # Save to DB
        if session.get("user_id"):
            new_performance = UserPerformance(
                user_id=session["user_id"],
                analyzed_name=session["analyzed_name"],
                marks_json=json.dumps(subjects),
                performance_level=session["performance"]
            )
            db.session.add(new_performance)
            db.session.commit()
            session["current_perf_id"] = new_performance.id # Track active analysis
        return redirect(url_for("results"))

    return redirect(url_for("home"))


@app.route("/analyze", methods=["POST"])
def analyze():
    """Handle manual marks submission."""
    data = request.form.to_dict()

    user_name = data.pop("user_name", "User").strip() or "User"
    goal = data.pop("goal", "10th")
    stream = data.pop("stream", "")
    group = data.pop("group", "")

    # Define relevant subjects for each category to prevent cross-contamination
    # (Since hidden form fields are still submitted by default)
    relevant_subjects = []
    if goal == "10th":
        relevant_subjects = ["Mathematics", "Science", "English", "Social Science", "Gujarati", "Sanskrit"]
    else:
        if stream == "Science":
            if group == "A Group (Maths)":
                relevant_subjects = ["English", "Physics", "Physics Practical", "Chemistry", "Chemistry Practical", "Mathematics", "Computer", "Computer Practical"]
            else:
                relevant_subjects = ["English", "Physics", "Physics Practical", "Chemistry", "Chemistry Practical", "Biology", "Biology Practical", "Computer", "Computer Practical"]
        else: # Commerce
            relevant_subjects = ["Element of Acc", "Economics", "Statistics", "Org. of Comm", "English", "Gujarati", "Computer", "Computer Practical"]

    # Build marks dict from relevant subject data only
    marks = {}
    for sub in relevant_subjects:
        val = data.get(f"mark_{sub}", "0")
        try:
            marks[sub] = int(val)
        except ValueError:
            marks[sub] = 0

    session["analyzed_name"] = user_name
    session["marks"] = marks
    session["marks_ready"] = True
    session["welcome_spoken"] = False
    # Only eligible for welcome speech if voice is already ON when submitting
    session["welcome_eligible"] = get_settings().get("voice_enabled", False)

    # Determine performance title
    if goal == "10th":
        session["performance"] = "SSC Academic Performance"
    else:
        if stream == "Science":
            if group == "A Group (Maths)":
                session["performance"] = "HSC Science A Academic Performance"
            else:
                session["performance"] = "HSC Science B Academic Performance"
        else:
            session["performance"] = "HSC Commerce Academic Performance"
            
    # Save to DB
    if session.get("user_id"):
        new_performance = UserPerformance(
            user_id=session["user_id"],
            analyzed_name=session["analyzed_name"],
            marks_json=json.dumps(marks),
            performance_level=session["performance"]
        )
        db.session.add(new_performance)
        db.session.commit()
        session["current_perf_id"] = new_performance.id # Track active analysis

    return redirect(url_for("results"))


@app.route("/results")
def results():
    if not session.get("logged_in"):
        return redirect(url_for("welcome"))
    
    # Ensure user_id is present
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("welcome"))

    # Fetch latest performance if not in session (reduces session size)
    if not session.get("marks_ready") or not session.get("marks"):
        latest = UserPerformance.query.filter_by(user_id=user_id, is_hidden=False).order_by(UserPerformance.created_at.desc()).first()
        if latest:
            session["marks"] = json.loads(latest.marks_json)
            session["performance"] = latest.performance_level
            session["analyzed_name"] = latest.analyzed_name
            session["current_perf_id"] = latest.id
            session["marks_ready"] = True
            
    if not session.get("marks_ready"):
        return redirect(url_for("home"))

    # Fetch chat history directly from DB (Filtered by active performance)
    current_perf_id = session.get("current_perf_id")
    # Get chat history for this specific analysis, only non-hidden ones
    chat_history_rows = ChatHistory.query.filter_by(
        user_id=session["user_id"], 
        performance_id=session.get("current_perf_id"),
        is_hidden=False
    ).order_by(ChatHistory.timestamp.asc()).all()

    settings = get_settings()
    name = extract_first_name(session.get("analyzed_name", session.get("user_name", "User")))
    lang = settings["language"]

    if lang == "Hindi":
        greeting = f"नमस्ते, {name}! 👋"
    elif lang == "Gujarati":
        greeting = f"નમસ્તે, {name}! 👋"
    else:
        greeting = f"Hello, {name}! 👋"

    # Welcome text for TTS (Only if voice was ON when analysis started)
    welcome_audio_b64 = None
    if not session.get("welcome_spoken", False) and settings["voice_enabled"] and session.get("welcome_eligible", False):
        if lang == "Hindi":
            welcome_text = f"नमस्ते {name}! मैंने आपके शैक्षणिक प्रदर्शन का विश्लेषण किया है। मैं आपको सही करियर मार्गदर्शन देने के लिए यहाँ हूँ।"
        elif lang == "Gujarati":
            welcome_text = f"નમસ્તે {name}! મેં તમારા શૈક્ષણિક પરિણામનું વિશ્લેષણ કર્યું છે. હું તમને યોગ્ય કારકિર્દી માર્ગદર્શન આપવા અહીં છું."
        else:
            welcome_text = f"Hello {name}! I have analyzed your academic performance. I am here to guide you towards the best career path."

        audio_path = speak_openai(welcome_text)
        if audio_path:
            with open(audio_path, "rb") as f:
                welcome_audio_b64 = base64.b64encode(f.read()).decode()
            try:
                os.remove(audio_path)
            except:
                pass
        session["welcome_spoken"] = True

    return render_template(
        "results.html",
        greeting=greeting,
        name=name,
        marks=session.get("marks", {}),
        performance=session.get("performance", ""),
        chat_history=chat_history_rows,
        settings=settings,
        welcome_audio=welcome_audio_b64
    )


@app.route("/api/chat", methods=["POST"])
def api_chat():
    """AJAX endpoint for AI chat."""
    body = request.get_json()
    question = body.get("question", "").strip()
    if not question:
        return jsonify({"error": "Empty question"}), 400

    settings = get_settings()
    lang = settings["language"]

    language_instruction = {
        "English": "Respond in English.",
        "Hindi": "Respond in Hindi language only.",
        "Gujarati": "Respond in Gujarati language only.",
    }

    # RAG: Context Injection
    user_id = session.get("user_id")
    user_marks = session.get("marks", {})
    performance_level = session.get("performance", "Academic Performance")
    
    # Retrieve relevant knowledge
    relevant_knowledge = []
    if "SSC" in performance_level:
        relevant_knowledge = CAREER_KNOWLEDGE.get("10th Standard", [])
    elif "HSC Science A" in performance_level:
        relevant_knowledge = CAREER_KNOWLEDGE.get("12th Science A Group (Maths)", [])
    elif "HSC Science B" in performance_level:
        relevant_knowledge = CAREER_KNOWLEDGE.get("12th Science B Group (Biology)", [])
    elif "HSC Commerce" in performance_level:
        relevant_knowledge = CAREER_KNOWLEDGE.get("12th Commerce", [])

    context = f"User Performance: {performance_level}\n"
    context += f"Marks: {json.dumps(user_marks)}\n"
    
    # ML Intel Injection
    ml_profile = analyze_strength_weakness(user_marks)
    context += f"ML Strength/Weakness Analysis: {json.dumps(ml_profile)}\n\n"
    
    context += "Relevant Career Paths from Database:\n"
    context += json.dumps(relevant_knowledge, indent=2)

    # Prepare prompt messages
    messages = [
        {
            "role": "system",
            "content": (
                f"You are a professional AI Career Counsellor for 'CareerVerse'. {language_instruction.get(lang, 'Respond in English.')}\n"
                "You were developed by Jainam Parikh, a Data Science Intern at DataVidwan. If asked about your origin or creator, you must state this clearly.\n\n"
                "CONTEXT:\n"
                f"{context}\n\n"
                "PERSONALIZATION RULES:\n"
                "1. You MUST actively reference the user's specific performance in your reasoning. Use phrases like 'Given your excellent score of [mark] in [subject]...' or 'Since you have a strong analytical profile (as shown in [cluster])...'.\n"
                "2. When suggesting a career path, explain WHY it fits the user's specific marks and strengths found in the ML analysis provided in the context.\n"
                "3. If a user is weak in a core subject for a certain career, suggest how they can improve or offer alternative paths that align better with their existing strengths.\n\n"
                "INSTRUCTIONS:\n"
                "1. If the user says something simple like 'ok', 'thanks', or 'hello', respond naturally as a friendly human counsellor. Mention one of their top strengths if it's the start of the chat.\n"
                "2. Provide deep 'Strength/Weakness' analysis and 'Career Mapping' whenever the user asks for guidance or at the start of a conversation.\n"
                "3. When suggesting paths, use the 'Relevant Career Paths' in the context and always mention 'Future Scope'.\n"
                "4. Be encouraging, professional, and data-driven.\n"
                f"5. Use the user's name ({session.get('user_name', 'User')}) occasionally to build rapport.\n"
                f"6. If the marksheet name ({session.get('analyzed_name', 'Student')}) is different from the account name, refer to the performance as belonging to '{session.get('analyzed_name', 'the student')}' appropriately.\n"
                "7. Maintain your identity as a tool developed by Jainam Parikh at DataVidwan. Never claim to be OpenAI or any other entity."
            )
        }
    ]

    # Add conversation history from DB for context
    if user_id:
        prev_chats = ChatHistory.query.filter_by(user_id=user_id, is_hidden=False).order_by(ChatHistory.timestamp.asc()).limit(10).all()
        for c in prev_chats:
            messages.append({"role": "assistant" if c.role == "ai" else "user", "content": c.content})

    # Add the current question
    messages.append({"role": "user", "content": question})

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.4
        )
        ai_reply = response.choices[0].message.content
    except Exception as e:
        ai_reply = f"AI failed to respond: {str(e)}"

    # Report Generation Logic
    report_url = None
    report_keywords = ["report", "download", "pdf", "generate", "document"]
    if any(k in question.lower() for k in report_keywords):
        report_id = f"report_{uuid.uuid4().hex[:8]}.pdf"
        output_dir = os.path.join("data", "reports")
        os.makedirs(output_dir, exist_ok=True)
        report_path = os.path.join(output_dir, report_id)
        
        try:
            generate_pdf_report(
                user_name=session.get("user_name", "User"),
                performance_level=performance_level,
                marks=user_marks,
                ml_profile=ml_profile,
                career_recommendations=relevant_knowledge,
                output_path=report_path
            )
            report_url = url_for('download_report', report_id=report_id)
            ai_reply += "\n\nI have generated your personalized Career Report. You can download the PDF below."
        except Exception as e:
            print(f"Report Generation Error: {e}")

    # Store in DB only (removed session["chat_history"] update)
    if settings["chat_enabled"]:
        # history = session.get("chat_history", [])
        # history.append({"user": question, "ai": ai_reply})
        # session["chat_history"] = history
        
        if session.get("user_id"):
            perf_id = session.get("current_perf_id")
            u_msg = ChatHistory(user_id=session["user_id"], performance_id=perf_id, role='user', content=question)
            ai_msg = ChatHistory(user_id=session["user_id"], performance_id=perf_id, role='ai', content=ai_reply)
            db.session.add(u_msg)
            db.session.add(ai_msg)
            db.session.commit()

    # TTS
    audio_b64 = None
    if settings["voice_enabled"]:
        audio_path = speak_openai(ai_reply)
        if audio_path:
            with open(audio_path, "rb") as f:
                audio_b64 = base64.b64encode(f.read()).decode()
            try:
                os.remove(audio_path)
            except:
                pass

    return jsonify({"reply": ai_reply, "audio": audio_b64, "report_url": report_url})


@app.route("/download/<report_id>")
def download_report(report_id):
    """Serve generated career reports."""
    report_dir = os.path.join("data", "reports")
    return send_from_directory(report_dir, report_id, as_attachment=True)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/settings", methods=["GET"])
def settings_page():
    settings = get_settings()
    return render_template("settings.html", settings=settings)


@app.route("/settings", methods=["POST"])
def save_settings():
    session["ai_style"] = request.form.get("ai_style", "Standard")
    session["ocr_mode"] = request.form.get("ocr_mode", "Balanced")
    session["chat_enabled"] = request.form.get("chat_enabled") == "on"
    session["voice_enabled"] = request.form.get("voice_enabled") == "on"
    session["voice_type"] = request.form.get("voice_type", "nova")
    session["language"] = request.form.get("language", "English")
    try:
        session["response_font_size"] = int(request.form.get("response_font_size", 16))
    except ValueError:
        session["response_font_size"] = 16
    
    flash("Changes saved successfully!", "success")
    return redirect(url_for("settings_page"))


@app.route("/reset", methods=["POST"])
def reset():
    session["marks_ready"] = False
    session["marks"] = {}
    # session["chat_history"] = []
    session["welcome_spoken"] = False
    session["performance"] = ""
    return redirect(url_for("home"))

@app.route("/clear-chat", methods=["POST"])
def clear_chat():
    if not session.get("logged_in") or not session.get("user_id"):
        return redirect(url_for("login"))
    
    user_id = session["user_id"]
    perf_id = session.get("current_perf_id")
    
    try:
        if perf_id:
            # Soft delete: update is_hidden to True instead of deleting
            ChatHistory.query.filter_by(user_id=user_id, performance_id=perf_id).update({ChatHistory.is_hidden: True})
            db.session.commit()
            flash("Chat history cleared successfully!", "success")
        else:
            flash("No active analysis to clear chat history for.", "info")
    except Exception as e:
        db.session.rollback()
        flash(f"Error clearing chat history: {e}", "error")
    
    return redirect(url_for("settings_page"))


@app.route("/clear-data", methods=["POST"])
def clear_data():
    if not session.get("logged_in") or not session.get("user_id"):
        return redirect(url_for("login"))
    
    user_id = session["user_id"]
    try:
        # Soft delete: update is_hidden to True instead of deleting
        ChatHistory.query.filter_by(user_id=user_id).update({ChatHistory.is_hidden: True})
        UserPerformance.query.filter_by(user_id=user_id).update({UserPerformance.is_hidden: True})
        db.session.commit()
        
        # Clear specific session data
        session.pop("marks", None)
        session.pop("performance", None)
        session.pop("marks_ready", None)
        session.pop("current_perf_id", None)
        
        db.session.commit()
        
        # Clear uploaded files
        data_dir = app.config["UPLOAD_FOLDER"]
        if os.path.exists(data_dir):
            for f in os.listdir(data_dir):
                try:
                    os.remove(os.path.join(data_dir, f))
                except:
                    pass
        
        flash("All stored data cleared successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error clearing data: {e}", "error")
        
    return redirect(url_for("home"))
    return redirect(url_for("settings_page"))


@app.route("/admin/history")
def admin_history():
    if not session.get("logged_in"):
        return redirect(url_for("welcome"))
    if not session.get("is_admin"):
        return redirect(url_for("home")) # Admins who aren't admins go home, not welcome
    
    # Calculate platform analytics
    stats = {
        "registered_users": User.query.count(),
        "verified_users": User.query.filter_by(is_verified=True).count(),
        "unverified_users": User.query.filter_by(is_verified=False).count(),
        "total_interactions": ChatHistory.query.count(),
        "total_reports": UserPerformance.query.count()
    }
    
    logins = LoginHistory.query.order_by(LoginHistory.login_at.desc()).limit(20).all()
    performances = UserPerformance.query.order_by(UserPerformance.created_at.desc()).limit(20).all()
    
    # Fetch unique users who have chat history
    chatted_users = User.query.join(ChatHistory).distinct().all()
    
    return render_template("admin_history.html", logins=logins, performances=performances, chatted_users=chatted_users, stats=stats)


@app.route("/api/admin/user-chats/<int:user_id>")
def admin_user_chats(user_id):
    if not session.get("is_admin"):
        return jsonify({"error": "Admin access required"}), 403
    
    chats = ChatHistory.query.filter_by(user_id=user_id).order_by(ChatHistory.timestamp.asc()).all()
    chat_list = [{
        "role": c.role,
        "content": c.content,
        "timestamp": c.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    } for c in chats]
    
    return jsonify({"chats": chat_list})


@app.route("/api/admin/users/<list_type>")
def admin_user_list(list_type):
    if not session.get("is_admin"):
        return jsonify({"error": "Admin access required"}), 403
    
    if list_type == 'verified':
        users = User.query.filter_by(is_verified=True).order_by(User.created_at.desc()).all()
    elif list_type == 'pending':
        users = User.query.filter_by(is_verified=False).order_by(User.created_at.desc()).all()
    else: # 'all' or default
        users = User.query.order_by(User.created_at.desc()).all()

    user_list = [{
        "id": u.id,
        "username": u.username,
        "email": u.email,
        "is_admin": u.is_admin,
        "is_verified": u.is_verified,
        "created_at": u.created_at.strftime('%Y-%m-%d %H:%M:%S')
    } for u in users]
    
    return jsonify({"users": user_list})


@app.route("/static/images/<path:filename>")
def serve_image(filename):
    return send_from_directory("static/images", filename)

@app.route("/api/view-marksheet/<path:filename>")
def view_marksheet(filename):
    return send_from_directory("data", filename)


@app.route("/load_history/<int:perf_id>")
def load_history(perf_id):
    """Load a previous analysis session."""
    if not session.get("logged_in"):
        return redirect(url_for("welcome"))
    
    perf = UserPerformance.query.filter_by(
        id=perf_id, 
        user_id=session["user_id"],
        is_hidden=False
    ).first()
    if perf:
        session["marks"] = json.loads(perf.marks_json)
        session["performance"] = perf.performance_level
        session["analyzed_name"] = perf.analyzed_name
        session["current_perf_id"] = perf.id
        session["marks_ready"] = True
        session["welcome_spoken"] = True # Don't speak welcome for history
    
    return redirect(url_for("results"))


@app.route("/new_analysis")
def new_analysis():
    """Clear current analysis and go to home."""
    session.pop("marks", None)
    session.pop("marks_ready", None)
    session.pop("performance", None)
    session.pop("analyzed_name", None)
    session.pop("current_perf_id", None)
    session.pop("welcome_spoken", None)
    return redirect(url_for("home"))

def ensure_db_exists():
    """Ensure the MySQL database exists before SQLAlchemy tries to connect."""
    uri = app.config.get('SQLALCHEMY_DATABASE_URI')
    if uri and 'mysql' in uri:
        try:
            url = make_url(uri)
            db_name = url.database
            host = url.host or 'localhost'
            user = url.username or 'root'
            password = url.password or ""
            
            print(f"DEBUG: Checking/Creating database '{db_name}' on {host}...")
            conn = pymysql.connect(host=host, user=user, password=password)
            conn.cursor().execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            conn.close()
            print(f"DEBUG: Database '{db_name}' is ready.")
        except Exception as e:
            print(f"DEBUG: Could not auto-create database: {e}. If it's your first time, please create database '{db_name}' manually in MySQL.")

@app.before_request
def create_tables():
    if not hasattr(app, 'tables_created'):
        try:
            ensure_db_exists()
            db.create_all()
            app.tables_created = True
        except Exception as e:
            print(f"DEBUG: Error during database initialization: {e}")
            # Note: app.tables_created will remain False, so it will retry on next request
            # which might help if it's a transient connection issue

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
