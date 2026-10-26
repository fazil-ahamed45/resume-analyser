import os
from app import create_app
from app.extensions import db

env = os.environ.get("FLASK_ENV", "development")
app = create_app(env)


@app.cli.command("init-db")
def init_db():
    """Initialize the SQLite database schema."""
    with app.app_context():
        db.create_all()
        print("Initialized database schema successfully.")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", 5000))
    print(f"\n==========================================")
    print(f"  CareerPilot AI is ready!")
    print(f"  Access the app at: http://127.0.0.1:{port}")
    print(f"  Or: http://localhost:{port}")
    print(f"==========================================\n")
    app.run(host=host, port=port, debug=True)
