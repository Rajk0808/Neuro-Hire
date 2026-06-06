import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#080b12",
        surface: "#10151f",
        panel: "#151b27",
        line: "#293241",
        primary: "#8ea1ff",
        teal: "#64d8cb",
        amber: "#ffbc73",
        rose: "#ff8fa3"
      },
      borderRadius: {
        md: "0.5rem"
      },
      fontFamily: {
        sans: ["Inter", "Arial", "sans-serif"]
      }
    }
  },
  plugins: []
};

export default config;
