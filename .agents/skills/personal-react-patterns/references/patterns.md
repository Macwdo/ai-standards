# React Pattern Matrix

Use this file when the task needs a quick boundary decision or a small implementation example.

## Decision Matrix

| Problem | Default tool | Notes |
| --- | --- | --- |
| Validate or parse input | `zod` | Define schema first and infer types where practical. |
| Multi-field validated form | `react-hook-form` + `zodResolver` | Keep schema next to the form or in a nearby contract module. |
| Remote read or mutation | `@tanstack/react-query` | Use query keys, invalidation, and mutation lifecycle instead of custom cache logic. |
| Shared client UI/workflow state | `zustand` | Use small focused stores with selectors. |
| Simple local toggle/input | Component state | Do not introduce heavier tooling for trivial state. |

## Example: Validated Form

Use `zod` to define the contract, infer the form values from the schema, and wire the form through `react-hook-form`.

```tsx
const profileSchema = z.object({
  name: z.string().min(1),
  email: z.email(),
})

type ProfileFormValues = z.infer<typeof profileSchema>

const form = useForm<ProfileFormValues>({
  resolver: zodResolver(profileSchema),
  defaultValues: {
    name: "",
    email: "",
  },
})
```

## Example: Server Data With Mutation

Keep remote state in React Query and invalidate the affected query after a successful mutation.

```tsx
const usersQuery = useQuery({
  queryKey: ["users"],
  queryFn: getUsers,
  staleTime: 30_000,
})

const createUserMutation = useMutation({
  mutationFn: createUser,
  onSuccess: async () => {
    await queryClient.invalidateQueries({ queryKey: ["users"] })
  },
})
```

## Example: Shared UI Store

Use Zustand for cross-component UI state that is not server data and not form state.

```tsx
type FilterStore = {
  search: string
  setSearch: (search: string) => void
}

export const useFilterStore = create<FilterStore>((set) => ({
  search: "",
  setSearch: (search) => set({ search }),
}))
```

## Anti-Patterns

- Do not cache API response bodies in Zustand.
- Do not mirror React Query results into Zustand unless there is a narrowly justified integration boundary.
- Do not wrap a trivial single search input in `react-hook-form`.
- Do not create a `zod` schema and then manually duplicate its type definitions unless a library boundary makes that unavoidable.
