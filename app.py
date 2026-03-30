from app import create_app

# Many host providers like Render/Vercel default to looking for 'app:app' 
# or 'app' in 'app.py' at the root.
app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5001)
