import type { Config } from 'tailwindcss';
const config: Config = {
  content: [
    './app/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './features/**/*.{ts,tsx}',
    './hooks/**/*.{ts,tsx}',
    './lib/**/*.{ts,tsx}',
    './services/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#11486b',
        secondary: '#f5f7fa',
        background: '#f5f7fa',
        success: '#478356',
        danger: '#ac2b49',
        orange: '#da6328',
        warning: '#ffa425',
        accent: '#ffa425',
        accentHover: '#e6951f',
        textPrimary: '#1f2937',
        textSecondary: '#6b7280',
        textMuted: '#9ca3af',
        border: '#e5e7eb',
        card: '#ffffff',
        surfaceAlt: '#f9fafb',
        dark: '#111827',
      },
      fontFamily: {
        sans: ['var(--font-geist-sans)', 'ui-sans-serif', 'system-ui'],
        mono: ['var(--font-geist-mono)', 'ui-monospace', 'monospace'],
        display: ['var(--font-geist-sans)', 'ui-sans-serif', 'system-ui'],
      },
    },
  },
  plugins: [],
};

export default config;
