import { Sparkles } from "lucide-react";
import { Button } from "@/components/atoms/Button";

export default function RegisterPage() {
  return (
    <main className="auth-page">
      <form className="panel auth-card">
        <Sparkles />
        <h1>Create Workspace</h1>
        <input placeholder="Company name" />
        <input placeholder="Recruiter email" type="email" />
        <input placeholder="Password" type="password" />
        <Button type="button">Provision agents</Button>
        <a href="/login">Already have access?</a>
      </form>
    </main>
  );
}
