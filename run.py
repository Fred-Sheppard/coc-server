from app import create_app
import os
app = create_app()

if __name__ == '__main__':
    url = os.environ.get('SERVER_URL', 'http://localhost:5000')
    port = int(url.split(':')[2])
    app.run(debug=True, host='0.0.0.0', port=port) 