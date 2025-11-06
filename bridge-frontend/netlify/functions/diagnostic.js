// ✅ Minimal verified Netlify Function
export default async () => {
  return new Response(
    JSON.stringify({ message: "Bridge runtime verified ✅" }),
    { headers: { "Content-Type": "application/json" } }
  );
};
