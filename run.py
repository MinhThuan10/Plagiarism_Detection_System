import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Lấy cổng từ biến môi trường hoặc mặc định là 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
