from mangum import Mangum
from brh.app import app

# Wrap FastAPI app for Netlify (AWS Lambda)
handler = Mangum(app)
