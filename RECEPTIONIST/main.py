
from app import app

if __name__ == '__main__':
    print("Starting The Kids Clinic - Receptionist System...")
    print("Server will be available at:")
    print("- Local: http://localhost:5000")
    print("- Network: http://192.168.1.11:5000")
    print("Press Ctrl+C to stop the server")
    app.run(host='0.0.0.0', port=5000, debug=True)
