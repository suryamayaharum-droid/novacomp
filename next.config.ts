import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  turbopack: {
    root: process.cwd(),
  },
  async rewrites() {
    return [
      {
        source: "/api/py/:path*",
        destination: process.env.PYTHON_API_URL 
          ? `${process.env.PYTHON_API_URL}/:path*`
          : "http://localhost:8000/api/:path*",
      },
    ];
  },
};

export default nextConfig;
