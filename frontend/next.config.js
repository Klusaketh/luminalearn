/**
 * Where the Next.js server forwards /api/v1 requests. Server-only: the browser always calls this
 * site's own /api/v1, so the backend's address never reaches client code. Change it in
 * .env.local (BACKEND_URL=...) if the backend runs on another host or port.
 */
const BACKEND_URL = (process.env.BACKEND_URL || "http://127.0.0.1:8001").replace(/\/+$/, "");
// The API proxy route (src/app/api/v1/[...path]/route.ts) reads the same value.
process.env.BACKEND_URL = BACKEND_URL;

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  ...(process.env.NEXT_OUTPUT === "standalone" ? { output: "standalone" } : {}),
  images: {
    domains: ["localhost"],
  },
  async rewrites() {
    return {
      // Route handlers can't accept WebSocket upgrades, so the voice socket is forwarded here.
      // Rewrites are fixed at build time: set BACKEND_URL before `next build` for production.
      beforeFiles: [{ source: "/api/v1/voice/:path*", destination: `${BACKEND_URL}/api/v1/voice/:path*` }],
    };
  },
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          {
            key: "X-Content-Type-Options",
            value: "nosniff",
          },
          {
            key: "X-Frame-Options",
            value: "DENY",
          },
          {
            key: "X-XSS-Protection",
            value: "1; mode=block",
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig;
