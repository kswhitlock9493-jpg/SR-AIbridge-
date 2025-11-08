// Bridge Runtime Handler (BRH) → Netlify Serverless Entrypoint

const path = require("path");

// Load backend FastAPI bridge
const resolver = require("../../../scripts/forge-resolver.js");

exports.handler = async (event, context) => {
  try {
    const response = await resolver.handle(event, context);
    return {
      statusCode: response.status || 200,
      headers: response.headers || { "Content-Type": "application/json" },
      body: typeof response.body === "string" ? response.body : JSON.stringify(response.body),
    };
  } catch (err) {
    return {
      statusCode: 500,
      body: JSON.stringify({
        error: "BRH_RUNTIME_FAILURE",
        message: err.message,
      }),
    };
  }
};
