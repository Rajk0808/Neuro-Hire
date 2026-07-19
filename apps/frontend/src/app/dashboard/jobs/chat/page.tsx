import { ChatPage } from "@/components/organisms/JDChatPanel";

interface PageProps {
  searchParams: Promise<{ q?: string }>;
}

export default async function ChatJobPage({ searchParams }: PageProps) {
  // Await searchParams as required by Next.js App Router conventions
  const resolvedParams = await searchParams;
  const initialQuery = resolvedParams.q || "";

  return (
    <div className="page-pad">
      <ChatPage initialQuery={initialQuery} />
    </div>
  );
}