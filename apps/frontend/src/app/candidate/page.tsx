import { CandidatePortalLayout } from "@/components/templates/CandidatePortalLayout";
import { Button } from "@/components/atoms/Button";
import Link from "next/link";

export default function CandidatePage() {
  return (
    <CandidatePortalLayout>
      <section className="panel candidate-welcome scanline">
        <h1>Your hiring companion is ready.</h1>
        <p>Track interview steps, ask role questions, and receive transparent updates from NeuroHire agents.</p>
        <Link href="/candidate/demo-token"><Button>Open companion chat</Button></Link>
      </section>
    </CandidatePortalLayout>
  );
}
