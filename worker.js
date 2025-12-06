export default {
  async fetch(request, env, ctx) {
    // Let Cloudflare's asset handler serve index.html, app.py, data, etc.
    return env.ASSETS.fetch(request);
  },
};
