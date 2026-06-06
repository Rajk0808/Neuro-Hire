import { Bot } from "lucide-react";
import { Button } from "@/components/atoms/Button";

export default function LoginPage() {
  return (
    <main className="auth-page">
      <form className="panel auth-card">
        <Bot />
        <h1>Recruiter Login</h1>
        <input placeholder="Work email" type="email" />
        <input placeholder="Password" type="password" />
        <Button type="button">Enter NeuroHire</Button>
        <a href="/register">Create a recruiter workspace</a>
      </form>
    </main>
  );
}
