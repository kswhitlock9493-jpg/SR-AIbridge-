# Netlify Python function wrapper for FastAPI via Mangum (ASGI→Lambda)
from mangum import Mangum
from brh.app import app

handler = Mangum(app)
