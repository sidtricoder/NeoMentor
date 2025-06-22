import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

import { ThemeProvider } from '@/components/theme-provider';
import { AuthProvider } from '@/lib/auth-context';
import Navbar from '@/components/navbar';
import Footer from '@/components/footer';
import { Toaster } from '@/components/ui/toaster';
import AnimatedWaveBackground from '@/components/animated-wave-background';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'NeoMentor | AI-Powered Learning & Education Platform',
  description: 'Transform your learning journey with personalized educational videos powered by advanced AI.',
  icons: {
    icon: [
      { url: '/favicon.ico', sizes: 'any' },
      { url: '/neomentor-icon.png', type: 'image/png' },
    ],
    apple: '/neomentor-icon.png',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <AuthProvider>
            <div className="flex flex-col min-h-screen relative">
              <Navbar />
              <main className="flex-grow relative z-10">{children}</main>
              <div className="relative z-10">
                <Footer />
              </div>
              <Toaster />
              <AnimatedWaveBackground />
            </div>
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
