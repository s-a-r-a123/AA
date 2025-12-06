export default {
  async fetch(request, env, ctx) {
    return new Response(
      "Air Aware Static Worker Running — app served from index.html.",
      { headers: { "Content-Type": "text/plain" } }
    );
  },
};
