import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#0b1326",
        foreground: "#dae2fd",
        // Flat semantic tokens used as text-on-surface, text-on-surface-variant
        "on-surface": "#dae2fd",
        "on-surface-variant": "#948ea1",
        primary: {
          DEFAULT: "#cdbdff",
          container: "#7c4dff",
          on: "#370096",
          onContainer: "#fcf6ff",
          fixed: "#cdbdff",
        },
        secondary: {
          DEFAULT: "#bdf4ff",
          container: "#00e3fd",
          on: "#00363d",
          onContainer: "#00616d",
        },
        tertiary: {
          DEFAULT: "#b0c6ff",
          container: "#066bf1",
          on: "#002d6e",
          onContainer: "#f9f8ff",
        },
        surface: {
          DEFAULT: "#0b1326",
          bright: "#31394d",
          dim: "#0b1326",
          container: "#171f33",
          // Material Design 3 container hierarchy
          "container-low": "#131b30",
          "container-high": "#222a3d",
          high: "#222a3d",
          highest: "#2d3449",
        },
        error: {
          DEFAULT: "#ffb4ab",
          container: "#93000a",
          on: "#690005",
        },
        outline: {
          DEFAULT: "#948ea1",
          variant: "#494455",
        }
      },
      fontFamily: {
        sans: ["var(--font-inter)"],
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
    },
  },
  plugins: [],
};
export default config;
