import { create } from "zustand";

type AuthStore = {
  recruiter: string | null;
  setRecruiter: (name: string | null) => void;
};

export const useAuthStore = create<AuthStore>((set) => ({
  recruiter: "Kavya Rao",
  setRecruiter: (recruiter) => set({ recruiter })
}));
