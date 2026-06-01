import NextAuth from 'next-auth';
import Credentials from 'next-auth/providers/credentials';

export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: [
    Credentials({
      credentials: {
        email: {},
        password: {},
      },
      authorize: async (credentials) => {
        // This would connect to your backend API
        // For now, return a placeholder user
        if (credentials.email && credentials.password) {
          return {
            id: '1',
            email: credentials.email,
            name: 'Recruiter',
            access_token: 'placeholder_token',
          };
        }
        return null;
      },
    }),
  ],
  callbacks: {
    jwt: async ({ token, user }) => {
      if (user) {
        token.access_token = user.access_token;
      }
      return token;
    },
    session: async ({ session, token }) => {
      if (session.user) {
        session.user.access_token = token.access_token as string;
      }
      return session;
    },
  },
});
