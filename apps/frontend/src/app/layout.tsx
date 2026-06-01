import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import '@/styles/tokens.css';
import '@/styles/animations.css';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'NeuroHire - Autonomous Recruitment',
  description: 'AI-powered recruitment platform for intelligent hiring',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-background text-on-surface`}>
        {children}
      </body>
    </html>
  );
}
