import Link from "next/link";

export function CandidatePortalLayout({ children }: { children: React.ReactNode }) {
  return (
    <main className="candidate-portal">
      <nav>
        <Link className="brand" href="/">
          <span>NH</span>
          <strong>Candidate Companion</strong>
        </Link>
      </nav>
      {children}
    </main>
  );
}
