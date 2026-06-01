'use client';

import React from 'react';
import { useUIStore } from '@/store/uiStore';

interface DashboardLayoutProps {
  children: React.ReactNode;
  sidebar?: React.ReactNode;
  topBar?: React.ReactNode;
}

export const DashboardLayout: React.FC<DashboardLayoutProps> = ({
  children,
  sidebar,
  topBar,
}) => {
  const { sidebarOpen } = useUIStore();

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      {sidebar && (
        <aside
          className={`${
            sidebarOpen ? 'w-64' : 'w-0'
          } hidden md:flex flex-col bg-surface-container-low border-r border-outline-variant transition-all duration-300 z-40`}
        >
          {sidebar}
        </aside>
      )}

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Bar */}
        {topBar && (
          <header className="h-16 bg-background border-b border-outline-variant sticky top-0 z-30">
            {topBar}
          </header>
        )}

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto">{children}</main>
      </div>
    </div>
  );
};
