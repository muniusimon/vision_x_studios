import io
import os
import sys
import logging
from datetime import datetime
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_file
)
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm  # type: ignore

#from openai import OpenAI
from PIL import Image
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length

# Add the parent directory to sys.path
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "default-secret-key"
)  # Change this to a random secret key
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# Dummy database using dictionaries
users: dict[str, dict] = {}
sessions: dict[str, dict] = {}

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey("team.id"))
    team = db.relationship("Team", back_populates="members")

    def get_id(self):
        return str(self.id)  # Make sure this returns a string


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    members = db.relationship("User", back_populates="team")


@login_manager.user_loader
def load_user(user_id):
    if user_id.isdigit():
        return User.query.get(int(user_id))
    return User.query.filter_by(email=user_id).first()


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Logged in successfully.")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("index"))  # Changed from 'home' to 'index'
        flash("Invalid email or password")
    return render_template("login.html", form=form)


class SignupForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    submit = SubmitField("Sign Up")


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.password = generate_password_hash(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Account created successfully. Please log in.", "success")
        return redirect(url_for("login"))  # Redirect to login page after signup
    return render_template("signup.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("index"))  # Changed from 'home' to 'index'


# Initialize the OpenAI client
#client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Check if the API key is set
#if not client.api_key:
#    print("Warning: OPENAI_API_KEY is not set in the environment variables.")


UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/image-editing", methods=["GET", "POST"])
@login_required
def image_editing():
    if request.method == "POST":
        # Check if the post request has the file part
        if "image" not in request.files:
            return jsonify({"error": "No file part"}), 400
        file = request.files["image"]
        # If user does not select file, browser also
        # submit an empty part without filename
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400
        if file and allowed_file(file.filename):
            try:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(filepath)

                # Here you would process the image
                # For now, we'll just return the uploaded image path
                edited_image_url = f"/static/uploads/{filename}"

                return render_template(
                    "image_editing.html", edited_image=edited_image_url
                )
            except Exception as e:
                app.logger.error(f"An error occurred: {str(e)}")
                return jsonify({"error": str(e)}), 500
        else:
            return jsonify({"error": "File type not allowed"}), 400
    else:
        return render_template("image_editing.html")


@app.route("/animation")
@login_required
def animation():
    return render_template("animation.html")


@app.route("/audio-processing")
@login_required
def audio_processing():
    return render_template("audio_processing.html")


@app.route("/text-generation", methods=["GET", "POST"])
@login_required
def text_generation():
    generated_text = None
    if request.method == "POST":
        user_input = request.form["user_input"]
        if not client.api_key:
            generated_text = "Error: OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable."
        else:
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",  # Changed from "gpt-4" to "gpt-3.5-turbo"
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": user_input},
                    ],
                )
                generated_text = response.choices[0].message.content
            except Exception as e:
                generated_text = f"Error: {str(e)}"
    return render_template("text_generation.html", generated_text=generated_text)


# Route to handle OpenAI API requests
@app.route("/ask", methods=["POST"])
@login_required
def ask_openai():
    if not client.api_key:
        return jsonify(
            {
                "error": "OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable."
            }
        ), 500

    user_input = request.json.get("message")
    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Changed from "gpt-4" to "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_input},
            ],
        )
        answer = response.choices[0].message.content

        # Return the response to the client (as JSON)
        return jsonify({"response": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/explore-features")
def explore_features():
    if current_user.is_authenticated:
        # If user is logged in, redirect to the features page
        return redirect(url_for("features"))
    else:
        # If user is not logged in, redirect to login page with a next parameter
        flash("Please log in to explore our features.")
        return redirect(url_for("login", next=url_for("features")))


@app.route("/features")
@login_required
def features():
    # This is the actual features page, only accessible to logged-in users
    return render_template("features.html")


@app.route("/ai-art-generator", methods=["GET", "POST"])
@login_required
def ai_art_generator():
    if request.method == "POST":
        prompt = request.form["prompt"]
        try:
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            generated_art_url = response.data[0].url
            return render_template(
                "ai_art_generator.html", generated_art=generated_art_url
            )
        except Exception as e:
            flash(f"Error generating image: {str(e)}")
    return render_template("ai_art_generator.html")


@app.route("/ai-video-generator", methods=["GET", "POST"])
@login_required
def ai_video_generator():
    if request.method == "POST":
        image = request.files["image"]
        # Here you would process the image and generate a video
        # For now, we'll just return a placeholder message
        generated_video_url = "placeholder_video_url.mp4"
        return render_template(
            "ai_video_generator.html", generated_video=generated_video_url
        )
    return render_template("ai_video_generator.html")


@app.route("/transparent-png-generator", methods=["GET", "POST"])
@login_required
def transparent_png_generator():
    if request.method == "POST":
        image = request.files["image"]
        # Here you would process the image to remove the background
        # For now, we'll just return the original image
        img = Image.open(image)
        img_io = io.BytesIO()
        img.save(img_io, "PNG")
        img_io.seek(0)
        return send_file(img_io, mimetype="image/png")
    return render_template("transparent_png_generator.html")


@app.route("/ai-canvas", methods=["GET", "POST"])
@login_required
def ai_canvas():
    if request.method == "POST":
        # Here you would process the canvas data and apply AI enhancements
        # For now, we'll just return a placeholder message
        enhanced_image_url = "placeholder_enhanced_image_url.jpg"
        return render_template("ai_canvas.html", enhanced_image=enhanced_image_url)
    return render_template("ai_canvas.html")


@app.route("/3d-texture-generation", methods=["GET", "POST"])
@login_required
def texture_generation():
    if request.method == "POST":
        obj_file = request.files["obj_file"]
        # Here you would process the OBJ file and generate textures
        # For now, we'll just return a placeholder message
        generated_texture_url = "placeholder_texture_url.jpg"
        return render_template(
            "texture_generation.html", generated_texture=generated_texture_url
        )
    return render_template("texture_generation.html")


@app.route("/models")
def models():
    # List of available AI models
    ai_models = [
        "Leonardo Anime XL",
        "Leonardo Lightning XL",
        "Leonardo Kino XL",
        "Leonardo Diffusion XL",
        "Leonardo Vision XL",
        "AlbedoBase XL",
        "PhotoReal",
        "RPG v5",
        "DreamShaper v7",
        "SDXL 1.0",
        # ... add more models as needed
    ]
    return render_template("models.html", models=ai_models)


class ForumPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


@app.route("/community")
def community():
    posts = ForumPost.query.order_by(ForumPost.created_at.desc()).limit(10).all()
    return render_template("community.html", posts=posts)


@app.route("/create-post", methods=["GET", "POST"])
@login_required
def create_post():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        new_post = ForumPost(title=title, content=content, user_id=current_user.id)
        db.session.add(new_post)
        db.session.commit()

        # Post to Discord
        discord_webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
        if discord_webhook_url:
            webhook = discord.Webhook.from_url(
                discord_webhook_url, adapter=discord.RequestsWebhookAdapter()
            )
            webhook.send(
                f"New post: {title}\nBy: {current_user.username}\n{content[:100]}..."
            )

        flash("Post created successfully!")
        return redirect(url_for("community"))
    return render_template("create_post.html")


@app.route("/for-teams")
def for_teams():
    return render_template("for_teams.html")


@app.route("/for-developers")
def for_developers():
    return render_template("for_developers.html")


@app.route("/create-team", methods=["GET", "POST"])
@login_required
def create_team():
    if request.method == "POST":
        team_name = request.form["team_name"]
        new_team = Team(name=team_name)
        current_user.team = new_team
        db.session.add(new_team)
        db.session.commit()
        flash("Team created successfully!")
        return redirect(url_for("team_dashboard"))
    return render_template("create_team.html")


@app.route("/team-dashboard")
@login_required
def team_dashboard():
    if current_user.team:
        return render_template("team_dashboard.html", team=current_user.team)
    return redirect(url_for("create_team"))


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/generate_image", methods=["GET", "POST"])
@login_required
def generate_image():
    """Generate an image using OpenAI API."""
    if request.method == "POST":
        prompt = request.form["prompt"]
        try:
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            image_url = response.data[0].url
            # Use the image_url instead of creating a new image object
            return render_template("generate_image.html", image_url=image_url)
        except Exception as e:
            flash(f"Error generating image: {str(e)}", "error")
    return render_template("generate_image.html")


@app.route("/download_obj/<filename>")
@login_required
def download_obj(filename):
    """Download the generated 3D object file."""
    # Implement the logic to serve the file for download
    return send_file(f"path/to/generated/objects/{filename}", as_attachment=True)


class AIChatHistory(db.Model):
    """Model for AI chat history."""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        """String representation of the chat history."""
        return f"<AIChatHistory {self.id}>"


@app.route('/image-generation')
def image_generation():
    return render_template('image_generation.html')


if __name__ == "__main__":
    try:
        logger.info("Starting the application...")
        with app.app_context():
            logger.info("Dropping all database tables...")
            db.drop_all()
            logger.info("Creating all database tables...")
            db.create_all()
        logger.info("Running the Flask application...")
        app.run(debug=True)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        import traceback
        logger.error(traceback.format_exc())