export function CandidatePortalLayout({ children }: { children: React.ReactNode }) {
  return (
    <main className="candidate-portal">
      <nav>
        <a className="brand" href="/">
          <span>NH</span>
          <strong>Candidate Companion</strong>
        </a>
      </nav>
      {children}
    </main>
  );
}
