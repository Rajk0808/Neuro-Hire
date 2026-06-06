export const authConfig = {
  providers: [],
  session: { strategy: "jwt" as const },
  pages: {
    signIn: "/login"
  }
};
