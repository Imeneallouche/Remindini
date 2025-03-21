from app import create_app
import sys

app = create_app()
if "--no-reload" not in sys.argv:
    sys.argv.append("--no-reload")
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)