// next.config.js
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  env: {
    NEXT_PUBLIC_API_URL: "https://mandacaru-backend-i2ci.onrender.com",
  },
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "https://mandacaru-backend-i2ci.onrender.com/api/:path*",
      },
    ];
  },
};

export default nextConfig;
