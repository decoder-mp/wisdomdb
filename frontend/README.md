# Lore Frontend

Timeless, calm React frontend for Lore with strong reading ergonomics, graceful motion, and feature-based architecture.

## Stack

- React + TypeScript + Vite
- TailwindCSS
- React Router
- Axios
- TanStack Query
- React Hook Form + Zod
- Framer Motion
- Lucide Icons

## Run

1. Install Node.js 20+
2. In this folder run npm install
3. Copy .env.example to .env
4. Run npm run dev

## App Structure

- src/app: providers and routing
- src/components: reusable UI and layout primitives
- src/features: domain slices (auth, lore, notifications, recommendations)
- src/pages: top-level screens
- src/lib: axios client, utilities
- src/types: shared types
- src/assets/logos: full logo set (light, dark, icon, monochrome)

## Core Design Notes

- Earth-toned palette with calm contrast
- Reading-first typography with generous line-height
- Intentional motion (no addictive bounce patterns)
- Functional navigation and information density inspired by professional tools
