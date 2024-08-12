from fantasyApp import create_app

app = create_app()


# Set up Celery
celery_app = app.extensions["celery"]

if __name__ == "__main__":
    app.run(debug=True)
