// ✅ Minimal verified Netlify Function
export default async (req, context) => {
  return new Response(
    JSON.stringify({ message: "Bridge runtime verified ✅" }),
    { headers: { "Content-Type": "application/json" } }
  );
};
