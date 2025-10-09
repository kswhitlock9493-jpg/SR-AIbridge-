// Minimal function to confirm functions bundling & path
export const handler = async () => {
  return {
    statusCode: 200,
    body: JSON.stringify({ ok: true, msg: "hello from functions" })
  };
};
