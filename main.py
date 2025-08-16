from app import app

if __name__ == '__main__':
    # Run Flask development server for network access
    app.run(host='0.0.0.0', port=5000, debug=False)
