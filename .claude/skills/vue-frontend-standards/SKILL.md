---
name: vue-frontend-standards
description: Apply project conventions for Vue.js frontend code — Vue 3.5+, TypeScript strict, Vite, Pinia setup stores, Vue Router, Tailwind CSS, ofetch + Zod, vee-validate, Vitest + Playwright. Auto-invoke when creating or reviewing Vue components, when working with .vue files, vite.config.ts, Pinia stores, Vue Router setup, Tailwind config, or when discussing Vue component structure, composables, frontend state management, forms, or styling. Do NOT load for backend Node.js services (use node-typescript-standards) or non-Vue frontend frameworks (React, Svelte, etc).
---

# Vue.js & Frontend Standarder

Følg disse konventioner for alle Vue.js-frontends. Vue 3.5+ med TypeScript er minimum.

## Tooling — eksplicit valg

| Område | Værktøj | Note |
|---|---|---|
| Framework | **Vue 3.5+** | Composition API only, `<script setup lang="ts">` |
| Build tool | **Vite** | Med `@vitejs/plugin-vue` |
| Sprog | **TypeScript strict** | Aldrig `<script>` uden `lang="ts"` |
| Package manager | **pnpm** | Pinnes via `packageManager` (corepack) |
| State | **Pinia** | Setup stores (`defineStore('foo', () => ...)`) |
| Routing | **Vue Router 4** | Lazy-loaded routes |
| Styling | **Tailwind CSS** | Util-first, `<style scoped>` til komplekse layouts |
| HTTP-klient | **ofetch** | Fra UnJS, bedre end fetch/axios |
| Validering | **Zod** | API-svar og forms valideres |
| Forms | **vee-validate** + Zod | `toTypedSchema(zod)` for type-sikkerhed |
| Linter | **ESLint flat config** | Med `eslint-plugin-vue` + `@vue/eslint-config-typescript` |
| Formatter | **Prettier** | Med `prettier-plugin-tailwindcss` |
| Test (unit) | **Vitest** + Vue Test Utils | ESM-native, hurtig |
| Test (E2E) | **Playwright** | Cross-browser, stabil |
| Imports | **Eksplicitte** | Ingen `unplugin-auto-import`-magi |

## Projekt-struktur (flad)

```text
projekt-navn/
├── src/
│   ├── assets/                 # Statiske filer (billeder, fonts)
│   ├── components/             # Genbrugelige komponenter (PascalCase.vue)
│   ├── composables/            # Genbrugelig logik (use-prefix)
│   ├── services/               # ofetch-klienter, API-kald
│   ├── schemas/                # Zod-skemaer (delt mellem services og forms)
│   ├── router/                 # Vue Router config + guards
│   │   └── index.ts
│   ├── stores/                 # Pinia setup stores
│   ├── views/                  # Side-komponenter (en per route)
│   ├── App.vue
│   ├── main.ts
│   └── style.css               # Tailwind directives + globals
├── tests/
│   ├── unit/                   # Vitest + VTU
│   └── e2e/                    # Playwright
├── public/
├── .node-version
├── .env.example                # VITE_-prefixed variabler
├── eslint.config.js
├── index.html
├── package.json
├── pnpm-lock.yaml              # SKAL committes
├── tailwind.config.js
├── tsconfig.json
├── vite.config.ts
└── README.md
```

## `tsconfig.json` — minimum-skelet

```json
{
  "compilerOptions": {
    "target": "ES2023",
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "lib": ["ES2023", "DOM", "DOM.Iterable"],
    "jsx": "preserve",
    "types": ["vite/client"],

    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,

    "skipLibCheck": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "useDefineForClassFields": true,

    "paths": { "@/*": ["./src/*"] }
  },
  "include": ["src/**/*", "src/**/*.vue"],
  "exclude": ["node_modules", "dist"]
}
```

## Component-konventioner

- **Altid `<script setup lang="ts">`** — Options API kun acceptabelt i legacy-kode der migreres.
- **Filnavngivning:** PascalCase for komponenter (`UserCard.vue`), kebab-case for views hvis route-baseret er OK.
- **Props:** Typed `defineProps<{}>()` med generic — ikke runtime object syntax.
  ```ts
  const props = defineProps<{ user: User; compact?: boolean }>()
  ```
- **Emits:** Typed `defineEmits<{}>()`.
  ```ts
  const emit = defineEmits<{ submit: [value: string]; cancel: [] }>()
  ```
- **Two-way binding:** Brug `defineModel()` (Vue 3.4+) — ikke `v-model` med manuel `update:modelValue`.
- **Komponent-størrelse:** Hvis en `.vue`-fil bliver over ~200 linjer, split den op (ekstrahér child component eller composable).
- **Direkte DOM-manipulation:** Forbudt. Brug `ref` på elementer, eller en composable.

## Composables-konventioner

- **Placering:** Genbrugelige i `composables/` med `useFoo.ts`-navn. Komponent-specifikke composables må ligge ved siden af komponenten.
- **Naming:** Altid `use`-prefix (`useUser`, `useFetchPosts`, `useDebounce`).
- **Return:** Returnér et objekt (`{ data, error, loading }`), ikke en tuple. Tuples mister navne ved destructuring.
- **Reaktivitet:** Hvis en composable tager input, skal det acceptere både `Ref<T>` og `T` — brug `MaybeRefOrGetter<T>` + `toValue()`.

## State management (Pinia)

- **Brug setup stores** — matcher `<script setup>`-mønstret og giver bedre TypeScript-inference:
  ```ts
  export const useUserStore = defineStore('user', () => {
    const user = ref<User | null>(null)
    const isLoggedIn = computed(() => user.value !== null)
    function login(u: User) { user.value = u }
    return { user, isLoggedIn, login }
  })
  ```
- **Lokal state hører til i komponenten.** Pinia er kun for state der deles på tværs af komponenter eller skal persisteres.
- **Naming:** Stores er `useFooStore`, eksporteret fra `stores/foo.ts`.

## HTTP & validering

- **Klient:** `ofetch` med en wrapper i `services/api.ts` der sætter base URL, headers og fejlhåndtering centralt.
- **Validering:** Alle API-svar valideres med Zod ved system-grænsen. Skemaer i `schemas/`-mappen, så de kan deles mellem services og forms.
  ```ts
  const UserSchema = z.object({ id: z.string(), name: z.string() })
  type User = z.infer<typeof UserSchema>

  export async function fetchUser(id: string): Promise<User> {
    const data = await api(`/users/${id}`)
    return UserSchema.parse(data)
  }
  ```
- **Direkte `fetch` eller `axios`** er forbudt — gå altid gennem `services/`-laget.

## Forms

- **vee-validate + Zod via `toTypedSchema`:**
  ```ts
  import { useForm } from 'vee-validate'
  import { toTypedSchema } from '@vee-validate/zod'

  const { handleSubmit, errors } = useForm({
    validationSchema: toTypedSchema(LoginSchema),
  })
  ```
- Genbrug Zod-skemaer fra `schemas/` — samme skema validerer både API-input og form-input.

## Routing

- **Lazy-load alle routes:** `component: () => import('@/views/UserView.vue')`.
- **Route meta** til auth/breadcrumbs: `meta: { requiresAuth: true }`.
- **Navigation guards** i `router/index.ts`, ikke spredt i komponenter.
- **Route-naming:** Kebab-case for paths (`/user-settings`), camelCase for `name` (`userSettings`).

## Styling (Tailwind)

- **Tailwind først, scoped CSS når nødvendigt.** Hvis en util-class-kæde bliver længere end ~5 classes og gentages, ekstrahér til en komponent — ikke til `@apply`.
- **`@apply`** er kun acceptabelt i `style.css` til virkelig globale primitives (links, focus-rings) — ikke til komponent-styling.
- **Komplekse layouts** (animations, complex selectors) hører til `<style scoped>` i SFC'en.
- **`prettier-plugin-tailwindcss`** sorterer classes automatisk.

## Test-konventioner

- **Unit (Vitest + VTU):** Test komponenters output og adfærd, ikke implementation. Mock kun ved system-grænser (ofetch, router).
- **E2E (Playwright):** Test kritiske brugerflows. Ikke hver knap.
- **Coverage minimum 80 %** på composables og services. Komponenter er hardere — fokusér på dem med logik.
- **Filnavngivning:** `*.test.ts` for unit, `*.spec.ts` for E2E (Playwright-konvention).

## Workflow-kommandoer (pnpm)

```bash
pnpm dev                         # Vite dev server med HMR
pnpm build                       # Production build (vue-tsc + vite build)
pnpm preview                     # Preview production build
pnpm test                        # Vitest watch
pnpm test:e2e                    # Playwright
pnpm lint                        # ESLint
pnpm typecheck                   # vue-tsc --noEmit
```

## Anti-patterns — gør IKKE dette

- ❌ Options API i nye komponenter (Composition API + `<script setup>` altid)
- ❌ `<script>` uden `lang="ts"`
- ❌ `ref<any>` eller mistede typer
- ❌ Direkte DOM-manipulation (`document.getElementById`, `querySelector`)
- ❌ `v-html` med ikke-saniteret bruger-input (XSS-risiko)
- ❌ Globalt state via `provide/inject` i stedet for Pinia (kun OK til dependency injection af services)
- ❌ Mixins (forældet pattern — brug composables)
- ❌ Options stores i Pinia (brug setup stores)
- ❌ Direkte `fetch`/`axios` i komponenter (gå gennem `services/`)
- ❌ Validering kun på frontend (server skal også validere — men frontend skal *altid* validere det den modtager)
- ❌ `unplugin-auto-import` til Vue API'er (eksplicit `import { ref, computed } from 'vue'`)
- ❌ `@apply` til komponent-styling (brug Tailwind classes direkte eller ekstrahér komponent)
- ❌ `vue-class-component` eller decorator-baseret syntax (forældet)
- ❌ Manglende `key` på `v-for`
- ❌ `v-if` og `v-for` på samme element

## Note for fullstack-projekter

I et monorepo ligger frontenden i `/client/` med egen `package.json`, `node_modules` og `tsconfig.json` — aldrig delt med backend. Hvis backend er Node/TypeScript, skal `node-typescript-standards` også konsulteres for server-delen.

**Tip:** Zod-skemaer kan deles mellem `/client/src/schemas/` og `/server/src/.../schema.ts` via en lille fælles pakke (`/shared/schemas/`) — det giver én sandhed for kontrakten mellem frontend og backend.