import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import Providers from './providers';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'NeuroHire - AI-Powered Recruitment',
  description: 'Intelligent candidate matching and bias-aware hiring',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-background text-on-background`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
