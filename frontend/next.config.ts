import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  eslint: {
    // Disable ESLint during builds when DISABLE_ESLINT env var is set to 'true'
    ignoreDuringBuilds: process.env.DISABLE_ESLINT === 'true'
  }
};

export default nextConfig;
