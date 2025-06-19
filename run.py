# run.py
from app import create_app
import os
app = create_app()

if __name__ == '__main__':
    # app.run(debug=True)

    port = int(os.getenv('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
