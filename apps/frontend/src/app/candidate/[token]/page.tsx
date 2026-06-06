import { Bot, Send } from "lucide-react";
import { CandidatePortalLayout } from "@/components/templates/CandidatePortalLayout";
import { Button } from "@/components/atoms/Button";

export default async function CandidateTokenPage({ params }: { params: Promise<{ token: string }> }) {
  const { token } = await params;
  return (
    <CandidatePortalLayout>
      <section className="panel chat-panel">
        <div className="section-head">
          <div>
            <span>Secure token</span>
            <h1>Companion Chat</h1>
          </div>
          <small>{token}</small>
        </div>
        <div className="chat-message agent"><Bot /> Your technical interview is confirmed. I can help you prepare with role scope, panel format, and timeline.</div>
        <div className="chat-message user">What should I focus on?</div>
        <div className="chat-message agent"><Bot /> Expect ML systems design, evaluation strategy, and production debugging scenarios.</div>
        <div className="chat-input">
          <input placeholder="Ask your companion..." />
          <Button icon={<Send size={16} />}>Send</Button>
        </div>
      </section>
    </CandidatePortalLayout>
  );
}
