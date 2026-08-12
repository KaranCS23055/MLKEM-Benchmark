/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#F7F4EE', // Warm off-white / beige research background
        surface: '#FFFFFF',    // Clean white card background
        border: '#E2E8F0',     // Light gray border
        borderMuted: '#EAE7E1',
        navy: {
          50: '#F0F3F9',
          100: '#D9E2EC',
          800: '#1E293B',
          900: '#0F172A',
          950: '#090D16',
        },
        brand: {
          DEFAULT: '#0F172A',
          navy: '#1E3A8A',
          accent: '#2563EB',
        },
        status: {
          successBg: '#ECFDF5',
          successText: '#065F46',
          successBorder: '#A7F3D0',
          warningBg: '#FFFBEB',
          warningText: '#92400E',
          warningBorder: '#FDE68A',
          errorBg: '#FEF2F2',
          errorText: '#991B1B',
          errorBorder: '#FCA5A5',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Menlo', 'Monaco', 'Consolas', 'monospace'],
      },
      boxShadow: {
        'xs': '0 1px 2px 0 rgba(0, 0, 0, 0.03)',
        'sm': '0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px -1px rgba(0, 0, 0, 0.03)',
        'card': '0 1px 3px 0 rgba(15, 23, 42, 0.04), 0 1px 2px -1px rgba(15, 23, 42, 0.02)',
        'card-hover': '0 4px 12px 0 rgba(15, 23, 42, 0.06)',
      },
    },
  },
  plugins: [],
}
