/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  output: 'standalone',
  images: {
    domains: ['localhost', 'neomentor-backend-140655189111.us-central1.run.app'],
    unoptimized: false,
  },
}

module.exports = nextConfig
