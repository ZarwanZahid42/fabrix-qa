import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // FabriX-QA brand palette — deep navy + electric cyan accent
        brand: {
          900: '#0A0A14',
          800: '#0F0F23',
          700: '#161630',
          600: '#1E1E40',
          500: '#2A2A5A',
          accent: '#00D4FF',
          'accent-dim': '#0099BB',
          success: '#00E096',
          warning: '#FFB800',
          danger: '#FF4D6D',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
};

export default config;
