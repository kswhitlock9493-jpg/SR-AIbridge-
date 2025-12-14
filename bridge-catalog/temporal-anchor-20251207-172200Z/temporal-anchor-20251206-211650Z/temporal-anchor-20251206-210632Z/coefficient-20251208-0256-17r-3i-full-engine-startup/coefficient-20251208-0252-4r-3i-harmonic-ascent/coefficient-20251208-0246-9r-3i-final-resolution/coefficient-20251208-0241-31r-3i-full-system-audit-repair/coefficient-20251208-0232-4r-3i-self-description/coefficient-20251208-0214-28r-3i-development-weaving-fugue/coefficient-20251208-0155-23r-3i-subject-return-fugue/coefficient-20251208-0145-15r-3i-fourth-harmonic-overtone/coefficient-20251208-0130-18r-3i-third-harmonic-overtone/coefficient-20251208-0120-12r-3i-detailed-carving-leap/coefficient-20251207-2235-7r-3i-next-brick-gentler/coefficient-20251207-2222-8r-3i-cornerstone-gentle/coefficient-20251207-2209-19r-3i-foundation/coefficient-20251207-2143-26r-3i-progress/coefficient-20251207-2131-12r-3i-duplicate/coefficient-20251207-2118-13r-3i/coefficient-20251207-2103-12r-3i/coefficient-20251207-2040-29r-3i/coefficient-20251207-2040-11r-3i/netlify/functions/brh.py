from mangum import Mangum
from brh.app import app

# Wrap FastAPI in Mangum (Lambda adapter)
handler = Mangum(app)

# Netlify compatibility export
awsLambdaReceiver = handler
