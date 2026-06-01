'use client';

import React from 'react';

interface CandidatePortalLayoutProps {
  children: React.ReactNode;
  header?: React.ReactNode;
}

export const CandidatePortalLayout: React.FC<CandidatePortalLayoutProps> = ({
  children,
  header,
}) => {
  return (
    <div className="min-h-screen bg-background">
      {header && (
        <header className="bg-surface-container border-b border-outline-variant sticky top-0 z-30">
          {header}
        </header>
      )}
      <main className="max-w-2xl mx-auto p-6">{children}</main>
    </div>
  );
};
