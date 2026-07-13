import type { NextConfig } from "next";
//Useless Comment
const nextConfig: NextConfig = {
  reactStrictMode: true,
  // Linting is available via `npm run lint`; don't fail production builds on it.
  eslint: { ignoreDuringBuilds: true },
};

export default nextConfig;
