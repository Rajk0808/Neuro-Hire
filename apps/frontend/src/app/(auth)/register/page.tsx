"use client";

import { Sparkles } from "lucide-react";
import { Button } from "@/components/atoms/Button";
import { useState } from "react";
import { getApiErrorMessage, registerRecruiter } from "@/lib/api";

export default function RegisterPage() {
  const [companyName, setCompanyName] = useState<string>("");
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>("");
  const [message, setMessage] = useState<string>("");

  const handleRegister = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setMessage("");

    try {
      const response = await registerRecruiter({ companyName, email, password });
      setMessage(response.data.message || "Registration successful! Please check your email for verification.");
      window.setTimeout(() => {
        window.location.href = "/home";
      }, 600);
    } catch (err) {
      setError(getApiErrorMessage(err, "Unable to connect to the registration server."));
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="auth-page">
      <form className="panel auth-card" onSubmit={handleRegister}>
        <Sparkles />
        <h1>Create Workspace</h1>

        {error && <p className="auth-error">{error}</p>}
        {message && <p className="auth-success">{message}</p>}

        <input 
          placeholder="Company name" 
          type="text"
          required
          value={companyName}
          onChange={(e) => setCompanyName(e.target.value)}
        />
        <input 
          placeholder="Recruiter email" 
          type="email" 
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <input 
          placeholder="Password" 
          type="password" 
          required
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <Button type="submit" disabled={loading}>
          {loading ? "Provisioning..." : "Provision agents"}
        </Button>
        
        <a href="/login">Already have access?</a>
      </form>
    </main>
  );
}
