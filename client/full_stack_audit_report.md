# Full-Stack Audit Report — Internship Management System

> **Date:** 2026-04-26  
> **Stack:** Next.js 16 (Frontend) + FastAPI (Backend)  
> **Verdict:** The codebase is well-structured and professionally organized. Issues found are moderate in severity — mostly code duplication, a few unused components, minor security gaps, and deprecation warnings. No critical blockers.

---

## Executive Summary

| Area | Status | Issues |
|---|---|---|
| API Integration | ✅ Good | 1 minor endpoint mismatch (PUT vs PATCH) |
| Authentication Flow | ✅ Good | Token stored in `localStorage` (security note) |
| Data Flow | ✅ Good | End-to-end flows verified |
| TanStack Query | ⚠️ Fair | Underutilized — login/signup bypass it |
| Code Cleanup | ⚠️ Fair | 3 unused components, 3 duplicated functions, 1 unused schema |
| Folder Structure | ✅ Good | Clean modular separation |
| Reusability | ✅ Good | Shared UI components used consistently |
| Backend Validation | ✅ Good | Robust Pydantic schemas with validators |
| Performance | ✅ Good | Sensible query defaults, no major waste |
| Security | ⚠️ Fair | 3 findings (localStorage token, no 401 interceptor, deprecated API) |

---

## 1. API Integration Check

### ✅ Verified Endpoint Mappings

| Frontend Service | Method | Path | Backend Endpoint | Match |
|---|---|---|---|---|
| `auth.service.login` | POST | `/auth/login` | `POST /auth/login` | ✅ |
| `auth.service.signup` | POST | `/auth/signup` | `POST /auth/signup` | ✅ |
| `internship.service.getAll` | GET | `/internships/` | `GET /internships/` | ✅ |
| `internship.service.getById` | GET | `/internships/{id}` | `GET /internships/{id}` | ✅ |
| `application.service.applyToInternship` | POST | `/applications/` | `POST /applications/` | ✅ |
| `application.service.getMyApplications` | GET | `/applications/my` | `GET /applications/my` | ✅ |
| `application.service.getById` | GET | `/applications/{id}` | `GET /applications/{id}` | ✅ |
| `recommendation.service.getRecommendations` | POST | `/recommendations/` | `POST /recommendations/` | ✅ |

### ⚠️ Issue 1.1 — Internship Update Uses `PUT` Instead of `PATCH`

The backend defines `PUT /internships/{id}` for updates, but the `InternshipUpdate` schema uses partial updates (`exclude_unset=True`). REST convention for partial updates is `PATCH`.

**Location:** [internship.py:L103](file:///d:/internshipt/backned/api/v1/endpoints/internship.py#L103)

```diff
-@router.put("/{internship_id}", response_model=InternshipResponse, status_code=status.HTTP_200_OK)
+@router.patch("/{internship_id}", response_model=InternshipResponse, status_code=status.HTTP_200_OK)
```

### ⚠️ Issue 1.2 — Missing Frontend Services for Existing Endpoints

The following backend endpoints have **no frontend service functions**:

| Backend Endpoint | Purpose |
|---|---|
| `PATCH /applications/{id}/status` | Update application status (admin) |
| `POST /progress/` | Add progress log |
| `GET /progress/{application_id}` | Get progress logs |
| `POST /certificate/generate` | Generate certificate |
| `GET /certificate/{id}` | Download certificate |
| `GET /analytics/dashboard` | Dashboard analytics |
| `GET /analytics/users` | User analytics |
| `GET /analytics/internships` | Internship analytics |
| `GET /analytics/applications` | Application analytics |
| `PUT /internships/{id}` | Update internship (admin) |
| `DELETE /internships/{id}` | Delete internship (admin) |
| `POST /internships/` | Create internship (admin) |

**Impact:** These are needed for the admin panel and progress/certificate flows. The admin page is currently a placeholder.

**Recommendation:** Create these service functions when the admin UI and progress/certificate features are built. They're not dead code — they're backend-ready for upcoming frontend features.

### ✅ Issue 1.3 — Base URL & Environment

- Axios base URL correctly falls back to `http://localhost:8000/api/v1`
- Backend CORS allows `http://localhost:3000` ✅
- Backend router prefix is `/api/v1` ✅
- Environment variable `NEXT_PUBLIC_API_BASE_URL` is supported ✅

---

## 2. Authentication Flow

### ✅ What's Working Well

1. **JWT Flow:** Login → receives `access_token` → stored via `setToken()` → attached via axios interceptor ✅
2. **Dual Storage:** Token stored in both `localStorage` (for API calls) and `cookie` (for SSR middleware) ✅
3. **Middleware Protection:** Next.js middleware guards `/dashboard`, `/applications`, `/admin` routes ✅
4. **Role-Based Access:** Middleware decodes JWT to check admin role for `/admin` routes ✅
5. **AuthGuard Component:** Client-side protection with role-based gating ✅

### ⚠️ Issue 2.1 — No Axios 401 Response Interceptor

When a token expires, API calls will return 401 but the user remains on the page without feedback.

**File:** [axios.ts](file:///d:/internshipt/client/lib/axios.ts)

**Recommendation:** Add a response interceptor to handle 401s:

```typescript
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      removeToken();
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  },
);
```

### ⚠️ Issue 2.2 — Token in `localStorage` (Security Note)

Storing JWT in `localStorage` is susceptible to XSS attacks. This is a common trade-off for SPAs.

**Current mitigation:** No sensitive data is stored beyond the token. The Next.js middleware uses the cookie copy.

**Recommendation for production:** Consider `httpOnly` cookies set by the backend instead, which would require a backend change to the login response.

### ✅ Issue 2.3 — Login Redirect Logic

The login page correctly:
- Reads `?next=` parameter for post-login redirect
- Validates the redirect path (rejects `//` protocol-relative URLs)
- Redirects admins to `/admin`, students to `/dashboard`

---

## 3. Data Flow Validation

### ✅ Recommendation Flow
```
RecommendationForm → POST /recommendations/ → AI Engine → RecommendationList → RecommendationCard → Apply
```
Verified end-to-end. The `useMutation` correctly handles loading/error/success states.

### ✅ Application Flow
```
Apply Button → POST /applications/ → invalidateQueries(['my-applications']) → Dashboard refresh
```
Cache invalidation after apply is correctly wired in `RecommendationCard.tsx:L56`.

### ✅ Progress → Lifecycle → Certificate Flow
Backend logic is complete:
- Progress creates auto-transitions `SELECTED` → `IN_PROGRESS` → `COMPLETED`
- Certificate generation requires `COMPLETED` status
- PDF generation via `reportlab` is functional

**Note:** Frontend UI for progress and certificates is not yet built (expected — admin panel is placeholder).

---

## 4. TanStack Query Usage

### ✅ What's Done Right

| Usage | File | Correct |
|---|---|---|
| `useQuery` for fetching applications | [applications/page.tsx:L16](file:///d:/internshipt/client/app/applications/page.tsx#L16) | ✅ |
| `useMutation` for recommendations | [page.tsx:L62](file:///d:/internshipt/client/app/page.tsx#L62) | ✅ |
| `useMutation` for apply-to-internship | [RecommendationCard.tsx:L50](file:///d:/internshipt/client/features/recommendation/components/RecommendationCard.tsx#L50) | ✅ |
| Cache invalidation after apply | [RecommendationCard.tsx:L56](file:///d:/internshipt/client/features/recommendation/components/RecommendationCard.tsx#L56) | ✅ |
| Query client singleton pattern | [queryClient.ts](file:///d:/internshipt/client/lib/queryClient.ts) | ✅ |

### ⚠️ Issue 4.1 — Login Bypasses TanStack Query

Login uses a raw `api.post()` call inside `useAuth` instead of `useMutation`. This means no built-in loading/error states from the query layer.

**File:** [useAuth.ts:L102-L125](file:///d:/internshipt/client/hooks/useAuth.ts#L102-L125)

**Impact:** Low — the login page manually manages `isSubmitting` and `error` state, which works fine. However, for consistency, a `useMutation` wrapper would be cleaner.

### ⚠️ Issue 4.2 — `authService` Is Not Used for Login

The `useAuth` hook calls `api.post('/auth/login', ...)` directly instead of using `authService.login()`. This duplicates the API call definition.

**Files:** 
- [useAuth.ts:L103](file:///d:/internshipt/client/hooks/useAuth.ts#L103) — Direct call
- [auth.service.ts:L29](file:///d:/internshipt/client/services/auth.service.ts#L29) — Service definition (partially unused for login)

**Recommendation:** Refactor `useAuth.login()` to use `authService.login()`:

```typescript
const login = useCallback(async ({ email, password }: LoginArgs): Promise<LoginResult> => {
  const data = await authService.login({ email, password });
  
  if (!data.access_token) {
    throw new Error('Login response does not include an access token');
  }

  setToken(data.access_token);
  const resolvedRole = normalizeRole(data.user?.role) ?? normalizeRole(decodeTokenPayload(data.access_token)?.role);
  storeRole(resolvedRole);

  return { token: data.access_token, role: resolvedRole };
}, []);
```

---

## 5. Code Cleanup

### 🔴 Issue 5.1 — Unused Components (Dead Code)

| Component | Location | Used By |
|---|---|---|
| `LoginForm` | [features/auth/LoginForm.tsx](file:///d:/internshipt/client/features/auth/LoginForm.tsx) | ❌ Not imported anywhere |
| `RegisterForm` | [features/auth/RegisterForm.tsx](file:///d:/internshipt/client/features/auth/RegisterForm.tsx) | ❌ Not imported anywhere |
| `InternshipList` + `InternshipCard` | [features/internship/](file:///d:/internshipt/client/features/internship) | ❌ Not imported in any page |

**Analysis:**
- `LoginForm` is a duplicate of the inline form in `app/login/page.tsx`. The login page builds its own form instead of using this component.
- `RegisterForm` exists but there's no `/register` route.
- `InternshipList` / `InternshipCard` are ready-made components but no browse/listing page exists yet.

**Recommendation:** 
- **Delete** `features/auth/LoginForm.tsx` — refactor `app/login/page.tsx` to use reusable Input components (it currently uses raw `<input>` elements)
- **Keep** `RegisterForm` — will be needed when `/register` route is created
- **Keep** `InternshipList` / `InternshipCard` — will be needed for the browse internships page

### 🔴 Issue 5.2 — Unused Schema Class

| Schema | Location | Used By |
|---|---|---|
| `TokenPayload` | [auth_schema.py:L50](file:///d:/internshipt/backned/schemas/auth_schema.py#L50) | ❌ Never imported |

**Recommendation:** Remove `TokenPayload` or use it in `decode_access_token()` for payload validation.

### 🔴 Issue 5.3 — Duplicated Utility Functions (Backend)

The function `_normalize_optional_text()` is **identically defined** in 3 files:
- [internship_schema.py:L6](file:///d:/internshipt/backned/schemas/internship_schema.py#L6)
- [progress_schema.py:L6](file:///d:/internshipt/backned/schemas/progress_schema.py#L6)
- [recommendation_schema.py:L4](file:///d:/internshipt/backned/schemas/recommendation_schema.py#L4)

The function `_normalize_skills()` is **identically defined** in 2 files:
- [internship_schema.py:L16](file:///d:/internshipt/backned/schemas/internship_schema.py#L16)
- [recommendation_schema.py:L15](file:///d:/internshipt/backned/schemas/recommendation_schema.py#L15)

**Recommendation:** Extract to a shared `schemas/validators.py` module:

```python
# schemas/validators.py

def normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    if not normalized:
        raise ValueError("Field must not be empty")
    return normalized


def normalize_skills(skills: list[str] | None) -> list[str] | None:
    if skills is None:
        return None
    normalized_skills: list[str] = []
    seen: set[str] = set()
    for skill in skills:
        normalized = skill.strip()
        if not normalized:
            continue
        lowered = normalized.lower()
        if lowered not in seen:
            seen.add(lowered)
            normalized_skills.append(normalized)
    if not normalized_skills:
        raise ValueError("At least one non-empty skill is required")
    return normalized_skills
```

### ⚠️ Issue 5.4 — Redundant CSS File

[styles/globals.css](file:///d:/internshipt/client/styles/globals.css) only contains a comment — it serves no purpose.

**Recommendation:** Delete `styles/globals.css` and the `styles/` directory.

### ⚠️ Issue 5.5 — Login Page Uses Raw Inputs Instead of Reusable `<Input />`

The login page ([app/login/page.tsx:L104-L128](file:///d:/internshipt/client/app/login/page.tsx#L104-L128)) manually creates `<input>` elements with inline className strings instead of using the reusable `<Input />` component from `components/ui/Input.tsx`.

**Recommendation:** Refactor to use `<Input />` for consistency.

### ✅ No Console.log Statements

No `console.log` statements found in user-written source code. ✅

### ✅ No Print Statements

No `print()` statements found in backend code. ✅

---

## 6. Folder Structure Validation

### ✅ Current Structure — Clean and Modular

```
client/
├── app/                    # Next.js App Router pages
│   ├── admin/page.tsx
│   ├── applications/page.tsx
│   ├── dashboard/page.tsx
│   ├── login/page.tsx
│   ├── layout.tsx
│   ├── page.tsx
│   └── globals.css
├── components/             # Shared reusable components
│   ├── auth/AuthGuard.tsx
│   ├── layout/{Navbar,Footer,Providers}.tsx
│   └── ui/{Button,Card,Input}.tsx
├── features/               # Feature-specific components
│   ├── application/{ApplicationCard,ApplicationList,StatusBadge}.tsx
│   ├── auth/{LoginForm,RegisterForm}.tsx
│   ├── internship/{InternshipCard,InternshipList}.tsx
│   └── recommendation/{RecommendationForm,RecommendationList,components/RecommendationCard}.tsx
├── hooks/useAuth.ts        # Custom hooks
├── lib/{axios,queryClient}.ts  # Infrastructure/configuration
├── services/               # API service layer
│   ├── auth.service.ts
│   ├── application.service.ts
│   ├── internship.service.ts
│   └── recommendation.service.ts
└── middleware.ts            # Route protection

backned/
├── api/v1/endpoints/       # Route handlers
├── core/{config,database,security}.py  # App configuration
├── models/                 # SQLAlchemy models
├── schemas/                # Pydantic schemas
├── services/               # Business logic
├── repositories/           # Data access layer
├── ai/                     # AI recommendation engine
├── analytics/              # Analytics schemas
└── utils/                  # Utilities (PDF generation)
```

**Verdict:** Excellent separation of concerns. Backend follows clean architecture (Router → Service → Repository). Frontend follows feature-based organization with shared components.

### ⚠️ Issue 6.1 — Directory Name Typo

The backend directory is named `backned` instead of `backend`.

**Recommendation:** Rename to `backend` if feasible (may require updating deployment scripts).

---

## 7. Reusability Check

### ✅ Shared UI Components

| Component | Used In |
|---|---|
| `Button` | Navbar, Dashboard, Applications, Admin, Login, RecommendationForm, RecommendationCard, InternshipCard |
| `Card` | Home, Dashboard, Admin, RecommendationForm, LoginForm, RegisterForm |
| `Input` | RecommendationForm, LoginForm, RegisterForm |

All three core UI components are well-parameterized with variants, loading states, and accessibility attributes.

### ⚠️ Issue 7.1 — Duplicate Error Display Pattern

The error display pattern (red border, bg-red-50, text-danger) is repeated in:
- LoginContent, LoginForm, RegisterForm, ApplicationList, InternshipList, RecommendationList

**Recommendation:** Extract to a shared `<Alert />` or `<ErrorBanner />` component:

```tsx
export default function ErrorBanner({ message, hint }: { message: string; hint?: string }) {
  return (
    <div className="rounded-xl border border-danger/20 bg-red-50 px-6 py-5 text-center">
      <p className="text-sm font-medium text-danger">{message}</p>
      {hint && <p className="mt-1 text-xs text-red-400">{hint}</p>}
    </div>
  );
}
```

---

## 8. Backend Validation (FastAPI)

### ✅ Strengths

1. **All endpoints reachable** — 7 routers correctly mounted with `/api/v1` prefix
2. **Pydantic validation** — Comprehensive field validators on all schemas
3. **Proper status codes** — 201 for creation, 204 for deletion, 409 for conflicts
4. **Error handling** — Custom exception classes with proper HTTP mapping
5. **Database relationships** — Foreign keys with `CASCADE` delete, unique constraints
6. **Role-based access** — `require_roles()` dependency for admin endpoints

### ⚠️ Issue 8.1 — `datetime.utcnow()` is Deprecated

Python 3.12+ deprecates `datetime.utcnow()`. Found in 3 locations:

| File | Line |
|---|---|
| [pdf_generator.py:L55](file:///d:/internshipt/backned/utils/pdf_generator.py#L55) | `datetime.utcnow().strftime(...)` |
| [analytics_repository.py:L23](file:///d:/internshipt/backned/repositories/analytics_repository.py#L23) | `datetime.utcnow() - timedelta(...)` |
| [analytics_repository.py:L188](file:///d:/internshipt/backned/repositories/analytics_repository.py#L188) | `now = datetime.utcnow()` |

**Fix:** Replace with `datetime.now(timezone.utc)`:

```diff
-from datetime import datetime, timedelta
+from datetime import datetime, timedelta, timezone

-active_cutoff = datetime.utcnow() - timedelta(days=active_window_days)
+active_cutoff = datetime.now(timezone.utc) - timedelta(days=active_window_days)
```

### ⚠️ Issue 8.2 — `application.py` Endpoint Parameter Ordering

In [application.py:L76-L80](file:///d:/internshipt/backned/api/v1/endpoints/application.py#L76-L80), the `payload` parameter appears *after* a `Path()` parameter without `Depends()`. FastAPI requires non-default parameters before default ones, but more importantly, a body parameter after path parameters without `Body()` annotation could confuse FastAPI's parameter resolution.

```python
def update_application_status(
    application_id: int = Path(gt=0),
    payload: ApplicationStatusUpdateRequest,  # ← Body param after Path param (no default)
    ...
```

**Recommendation:** Move `payload` before `application_id` or annotate explicitly:

```python
def update_application_status(
    payload: ApplicationStatusUpdateRequest,
    application_id: int = Path(gt=0),
    ...
```

### ⚠️ Issue 8.3 — SQL Injection Risk in `ilike` Filters

In [internship_repository.py:L33-L36](file:///d:/internshipt/backned/repositories/internship_repository.py#L33-L36):

```python
query = query.filter(Internship.location.ilike(f"%{location}%"))
```

While SQLAlchemy parameterizes queries (so this is **not** a direct SQL injection), the `%` and `_` wildcard characters in user input are not escaped. A user could craft input like `%` to match all records.

**Recommendation:** Escape wildcards:

```python
def _escape_like(value: str) -> str:
    return value.replace("%", r"\%").replace("_", r"\_")

query = query.filter(Internship.location.ilike(f"%{_escape_like(location)}%", escape="\\"))
```

---

## 9. Performance Optimization

### ✅ What's Done Right

1. **Query stale time:** 60s prevents excessive refetching
2. **`refetchOnWindowFocus: false`:** Prevents unnecessary API calls on tab switch
3. **Database pool:** Configured with `pool_size=10`, `max_overflow=20`, `pool_pre_ping=True`
4. **Lazy loading:** QueryClient created once per browser session (singleton)
5. **Animations use CSS:** No JS-based animation libraries, pure CSS transforms

### ⚠️ Issue 9.1 — Recommendation Engine Scans All Internships

In [recommendation_service.py:L29](file:///d:/internshipt/backned/services/recommendation_service.py#L29):

```python
internships = self.internship_repository.list()  # Fetches ALL
active_internships = [i for i in internships if i.is_active]  # Filters in Python
```

**Recommendation:** Filter at the database level:

```python
# Add to InternshipRepository
def list_active(self) -> list[Internship]:
    return self.db.query(Internship).filter(Internship.is_active.is_(True)).all()
```

### ⚠️ Issue 9.2 — Skill Filtering Happens in Python, Not SQL

In [internship_service.py:L63-L68](file:///d:/internshipt/backned/services/internship_service.py#L63-L68), skill matching is done by loading all internships and filtering in-memory. For small datasets this is fine, but won't scale.

**Impact:** Low for current usage patterns. Consider PostgreSQL JSON operators for production scale.

---

## 10. Security Check

### ✅ Strengths

1. **Password hashing:** bcrypt with auto-generated salt ✅
2. **Password validation:** Requires uppercase, lowercase, digit, and special character ✅
3. **JWT expiry:** Configurable, defaults to 30 minutes ✅
4. **CORS:** Restricted to `http://localhost:3000` ✅
5. **Admin-only endpoints:** Protected by `require_roles(UserRole.admin)` ✅
6. **Path traversal protection:** Certificate download resolves paths safely ✅
7. **No sensitive data exposed:** Password hash never returned in API responses ✅

### ⚠️ Issue 10.1 — JWT Secret Key Validation

The `.env.example` has a placeholder secret: `replace_with_a_secure_secret_key_of_at_least_32_characters`

**Recommendation:** Add a startup check in `config.py`:

```python
@model_validator(mode="after")
def validate_secret_not_placeholder(self) -> "Settings":
    if "replace" in self.jwt_secret_key.lower():
        raise ValueError("JWT_SECRET_KEY must be changed from the default placeholder")
    return self
```

### ⚠️ Issue 10.2 — Open Redirect Prevention Incomplete

The login page's `getSafeRedirectPath()` checks for `//` but doesn't validate against other schemes:

```typescript
if (nextPath.startsWith('/') && !nextPath.startsWith('//')) {
  return nextPath;
}
```

A path like `/\example.com` could be treated as a redirect by some browsers. Add additional validation:

```typescript
const getSafeRedirectPath = (nextPath: string | null): string | null => {
  if (!nextPath) return null;
  if (nextPath.startsWith('/') && !nextPath.startsWith('//') && !nextPath.includes('\\')) {
    return nextPath;
  }
  return null;
};
```

---

## Summary of Recommended Actions

### 🔴 Must Fix (Production Blockers)

| # | Issue | Priority | Effort |
|---|---|---|---|
| 8.1 | Replace deprecated `datetime.utcnow()` | High | 5 min |
| 8.2 | Fix parameter ordering in `update_application_status` | High | 2 min |

### 🟡 Should Fix (Code Quality)

| # | Issue | Priority | Effort |
|---|---|---|---|
| 5.1 | Remove unused `LoginForm` component | Medium | 2 min |
| 5.2 | Remove unused `TokenPayload` schema | Medium | 1 min |
| 5.3 | Extract duplicated validators to shared module | Medium | 15 min |
| 5.4 | Delete empty `styles/globals.css` | Medium | 1 min |
| 5.5 | Refactor login page to use `<Input />` component | Medium | 10 min |
| 4.2 | Use `authService.login()` in `useAuth` hook | Medium | 5 min |
| 1.1 | Change `PUT` to `PATCH` for internship updates | Medium | 2 min |
| 2.1 | Add axios 401 response interceptor | Medium | 5 min |

### 🟢 Nice to Have (Optimization)

| # | Issue | Priority | Effort |
|---|---|---|---|
| 7.1 | Extract shared `<ErrorBanner />` component | Low | 10 min |
| 9.1 | Filter active internships at DB level | Low | 5 min |
| 8.3 | Escape LIKE wildcards in filters | Low | 5 min |
| 10.1 | Add JWT secret placeholder check | Low | 5 min |
| 10.2 | Strengthen open redirect prevention | Low | 2 min |
| 6.1 | Fix `backned` → `backend` typo | Low | Varies |

---

## Overall Assessment

**Grade: B+** — The codebase demonstrates solid engineering practices with clean architecture, proper separation of concerns, comprehensive validation, and production-aware patterns. The issues found are typical of a project in active development and are straightforward to address. The backend is more mature than the frontend (admin features, progress tracking, and certificate management are backend-complete but lack frontend UI).
