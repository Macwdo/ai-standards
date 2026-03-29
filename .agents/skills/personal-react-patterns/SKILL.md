---
name: personal-react-patterns
description: "Apply my default React and Next.js implementation patterns: use Zod for schemas and validation, React Hook Form for non-trivial forms, TanStack React Query for server state, and Zustand for shared client state. Use when building or refactoring React/Next.js features so Codex follows these boundaries and composes with $shadcn for UI work and $vercel-react-best-practices for performance-sensitive React code."
---

# Personal React Patterns

Use this skill when implementing feature code in React or Next.js after the app already exists.

Do not use this skill for project bootstrap. If the task is to start a new Next.js app with the preferred stack, use `$personal-new-next-app` instead.

## Core Rules

- Define `zod` schemas first when the feature needs validation, parsing, or a reusable client-side contract.
- Infer TypeScript types from `zod` schemas where practical instead of duplicating types by hand.
- Use `react-hook-form` with `zodResolver` for non-trivial forms.
- Keep simple one-field or throwaway inputs in local component state when `react-hook-form` would be unnecessary overhead.
- Use `@tanstack/react-query` for async server data, cache lifecycle, loading states, invalidation, and mutations.
- Do not store fetched server data in `zustand`.
- Use `zustand` for shared client-only UI or workflow state that spans multiple components.
- Keep purely local UI state in the component instead of promoting it to `zustand`.
- Keep Next.js server-first. Add `"use client"` only where forms, query providers, Zustand consumers, or interactive UI require it.

## Working Pattern

1. Classify the state before writing code: local UI state, form state, shared client workflow state, or server state.
2. Write the `zod` schema first if the feature needs validation or typed input/output boundaries.
3. Build forms with `react-hook-form` and `zodResolver`.
4. Model remote reads and writes with React Query before considering any client store.
5. Add a small Zustand store only if state must be shared across client components and does not belong to the server cache or the form.

## Skill Composition

- Use `$shadcn` for component selection, form UI composition, and shadcn-specific rules.
- Use `$vercel-react-best-practices` for React and Next.js performance guidance.
- Keep this skill focused on ownership boundaries and implementation defaults. Do not repeat the detailed rules from those skills here.

## What To Avoid

- Do not use Zustand as a general replacement for React Query.
- Do not use React Query for purely local UI state.
- Do not hand-roll validation when a `zod` schema is already needed.
- Do not manage multi-field validated forms with ad hoc `useState`.
- Do not create broad stores when a narrow selector-based Zustand store will do.

## Reference

Read `references/patterns.md` when you need the decision matrix, examples, or anti-pattern reminders.
