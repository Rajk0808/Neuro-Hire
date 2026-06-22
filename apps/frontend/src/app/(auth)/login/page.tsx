"use client";

import { Bot } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/atoms/Button";
import { getApiErrorMessage, loginRecruiter } from "@/lib/api";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading(true);
    setError("");
    setMessage("");

    try {
      const response = await loginRecruiter({ email, password });
      setMessage(response.data.message || "Login successful!");
      window.setTimeout(() => {
        window.location.href = "/home";
      }, 600);
    } catch (err) {
      setError(getApiErrorMessage(err, "Unable to connect to the login server."));
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="auth-page">
      <form className="panel auth-card" onSubmit={handleLogin}>
        <Bot />
        <h1>Recruiter Login</h1>
        {error && <p className="auth-error">{error}</p>}
        {message && <p className="auth-success">{message}</p>}
        <input
          placeholder="Work email"
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          required
        />
        <input
          placeholder="Password"
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          required
        />
        <Button type="submit" disabled={loading}>
          {loading ? "Checking access..." : "Enter NeuroHire"}
        </Button>
        <a href="/register">Create a recruiter workspace</a>
      </form>
    </main>
  );
}
