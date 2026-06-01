'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <aside className="w-64 bg-surface-container border-r border-outline-variant">
        <div className="p-6 space-y-8">
          {/* Logo */}
          <Link href="/" className="block font-bold text-xl text-primary">
            NeuroHire
          </Link>

          {/* Navigation */}
          <nav className="space-y-2">
            {[
              { href: '/dashboard', label: 'Overview' },
              { href: '/dashboard/jobs', label: 'Jobs' },
              { href: '/dashboard/candidates', label: 'Candidates' },
              { href: '/dashboard/interviews', label: 'Interviews' },
              { href: '/dashboard/analytics', label: 'Analytics' },
            ].map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="block px-4 py-2 rounded-lg text-on-surface hover:bg-surface-container-high transition-colors"
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Top Bar */}
        <header className="h-16 bg-surface-container border-b border-outline-variant flex items-center justify-between px-6 sticky top-0">
          <div />
          <button
            onClick={() => router.push('/auth/login')}
            className="text-sm font-medium px-4 py-2 rounded-lg bg-primary text-on-primary hover:opacity-90 transition-opacity"
          >
            Sign Out
          </button>
        </header>

        {/* Page Content */}
        <div className="flex-1 overflow-auto p-6">{children}</div>
      </main>
    </div>
  );
}
