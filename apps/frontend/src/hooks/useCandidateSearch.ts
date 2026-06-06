"use client";

import { useMemo, useState } from "react";
import { candidates } from "@/lib/mockData";

export function useCandidateSearch() {
  const [query, setQuery] = useState("");
  const results = useMemo(() => {
    const needle = query.toLowerCase();
    return candidates.filter((candidate) => [candidate.name, candidate.current_role, ...candidate.skills].join(" ").toLowerCase().includes(needle));
  }, [query]);

  return { query, setQuery, results };
}
