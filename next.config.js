/** @type {import('next').NextConfig} */
const nextConfig = {
  // Allow better-sqlite3 native module in API routes
  experimental: {
    serverComponentsExternalPackages: ["better-sqlite3"],
  },
};

module.exports = nextConfig;
