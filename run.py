# run.py
# waitress-serve --listen=127.0.0.1:8000 run:app
from app import create_app
from waitress import serve
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
