import type { Metadata } from "next";
import "./globals.css";
import "@/styles/tokens.css";
import "@/styles/animations.css";

export const metadata: Metadata = {
  title: "NeuroHire",
  description: "Autonomous recruiting intelligence command center"
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className="dark">
      <body>{children}</body>
    </html>
  );
}
