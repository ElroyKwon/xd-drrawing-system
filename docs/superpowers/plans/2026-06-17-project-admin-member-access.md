# Project Admin Member Access Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Project Admin member-access slice where existing mock members can be granted project-specific access roles for `Study_Project`.

**Architecture:** Keep `Project`, `Member`, and `ProjectMemberAccess` separate. Add a focused Project Admin feature area with local mock state, derived access rows, a right inspector, and an add-existing-member modal. Before code changes, update the project feature docs and pass the local planning gate.

**Tech Stack:** Vite, React, TypeScript, Vitest, Testing Library, lucide-react, local mock state only.

---

## File Structure

Create:

- `src/projectAdminData.ts`  
  Owns Project Admin domain types, role/status constants, local mock projects/members/access records, and small helper functions for joining/filtering access rows.

- `src/ProjectAdminView.tsx`  
  Owns the Project Admin UI slice: left rail, current-project context, member access table, right inspector, add-member modal, validation, and local access state.

- `src/ProjectAdminView.test.tsx`  
  Tests the Project Admin slice independently from the hub project-list screen.

- `docs/feature-notes/002-project-admin-member-access.md`  
  Feature note linking ACC references, scope, data model, user flow, and verification criteria.

Modify:

- `src/App.tsx`  
  Adds a small local navigation path from the existing project list to the Project Admin view. Does not add routing libraries.

- `src/App.test.tsx`  
  Adds one integration test proving the existing app can enter the Project Admin view from `Study_Project`.

- `src/styles.css`  
  Adds Project Admin layout, table, inspector, modal, and responsive styles. Keep the existing initial setup styles intact.

- `docs/PRD.md`
- `docs/TRD.md`
- `docs/UI_Spec.md`
- `docs/Data_Model.md`
- `docs/Task_List.md`
- `docs/Acceptance_Criteria.md`
- `docs/Test_Scenarios.md`
- `docs/Design_Map.md`
- `docs/User_Flow.md`
- `docs/Planning_Gate_Checklist.md`
- `SPEC.md`
- `PLAN.md`
- `CHECKS.md`
- `HUMAN_GATE.md`
- `EVIDENCE.md`
- `docs/sessions/NEXT_SESSION.md`

Commit granularity:

1. Docs/gate commit after Task 0.
2. Data model/helper commit after Task 1.
3. Project Admin view commit after Tasks 2-4.
4. App wiring/styles/docs/evidence commit after Tasks 5-6.

---

### Task 0: Feature Docs And Planning Gate

**Files:**
- Create: `docs/feature-notes/002-project-admin-member-access.md`
- Modify: `docs/PRD.md`
- Modify: `docs/TRD.md`
- Modify: `docs/UI_Spec.md`
- Modify: `docs/Data_Model.md`
- Modify: `docs/Task_List.md`
- Modify: `docs/Acceptance_Criteria.md`
- Modify: `docs/Test_Scenarios.md`
- Modify: `docs/Design_Map.md`
- Modify: `docs/User_Flow.md`
- Modify: `docs/Planning_Gate_Checklist.md`
- Modify: `SPEC.md`
- Modify: `PLAN.md`
- Modify: `CHECKS.md`
- Modify: `HUMAN_GATE.md`
- Modify: `EVIDENCE.md`

- [ ] **Step 1: Read the local loop instructions**

Read:

```powershell
Get-Content -Raw -Encoding UTF8 .\.agents\skills\development-loop-orchestrator\SKILL.md
Get-Content -Raw -Encoding UTF8 .\.agents\skills\feature-docs-scaffold\SKILL.md
Get-Content -Raw -Encoding UTF8 .\.agents\skills\planning-gate\SKILL.md
Get-Content -Raw -Encoding UTF8 .\docs\superpowers\specs\2026-06-17-project-admin-member-access-design.md
```

Expected: all four files are readable. Stop if any are missing.

- [ ] **Step 2: Create the feature note**

Create `docs/feature-notes/002-project-admin-member-access.md` with this content:

```markdown
# 002 - Project Admin Member Access

## Slice

`Project Admin - 프로젝트 접근 구성원 관리`

## Product Decision

`Project` and `Member` are peer-level resources. Access is granted through `ProjectMemberAccess`.

```text
Project
Member
ProjectMemberAccess
  - projectId
  - memberId
  - role
  - status
  - addedAt
```

## In Scope

- Current project context: `Study_Project`.
- Project Admin shell with `구성원` selected.
- Members with access to `Study_Project`.
- Search by member name or email.
- Row selection and right inspector.
- Add existing mock member modal.
- Role choices: `관리자`, `편집자`, `뷰어`.
- Duplicate project/member access validation.

## Out Of Scope

- Company information.
- New user creation.
- Email invite.
- Real auth/RBAC enforcement.
- DB/API persistence.
- Access deletion/revocation.
- Autodesk cloud/API.

## References

- `reference/acc-screenshots/ScreenShot Tool -20260612102437.png`
- `reference/acc-screenshots/Video Screen1781227558018.png`
- `reference/acc-analysis/_ACC-Build-화면분석-재현설계.md` sections `#2` and `#3`
- `docs/superpowers/specs/2026-06-17-project-admin-member-access-design.md`

## Verification

- `npm test`
- `npm run build`
- Browser desktop/narrow checks for Project Admin table, inspector, add modal, validation, duplicate handling, and console errors.
```
```

- [ ] **Step 3: Update the seven core feature docs**

Apply these exact requirement IDs across the docs:

```text
FR-PA-001 Render Project Admin member access view for Study_Project.
FR-PA-002 Show only members with ProjectMemberAccess for Study_Project.
FR-PA-003 Search project-access members by name or email.
FR-PA-004 Select a member row and show right inspector details.
FR-PA-005 Open add-existing-member modal.
FR-PA-006 Block add submit when no member is selected.
FR-PA-007 Block duplicate ProjectMemberAccess for the same project/member.
FR-PA-008 Add a valid existing member with selected role to Study_Project.
FR-PA-009 Keep Project, Member, and ProjectMemberAccess separate; exclude company/auth/DB/API.
```

Update each document with matching IDs:

```text
docs/PRD.md: add the Project Admin member access slice under the current product scope.
docs/TRD.md: document local mock state only and the three peer-level data types.
docs/UI_Spec.md: document left rail, table, right inspector, add modal, validation messages.
docs/Data_Model.md: add Project, Member, ProjectMemberAccess and duplicate rule.
docs/Task_List.md: add T-PA-001 through T-PA-009 mapping to FR-PA-001 through FR-PA-009.
docs/Acceptance_Criteria.md: add AC-PA-001 through AC-PA-009.
docs/Test_Scenarios.md: add TS-PA-001 through TS-PA-009.
docs/Design_Map.md: map ACC #2/#3 references and local spec to the UI sections.
docs/User_Flow.md: add enter Project Admin, search, select, add, duplicate validation, cancel flow.
docs/Planning_Gate_Checklist.md: add a new Project Admin gate section.
```

Use the local validation messages exactly:

```text
구성원을 선택하세요.
이미 이 프로젝트에 추가된 구성원입니다.
```

- [ ] **Step 4: Update root project tracking docs**

Update these files:

```text
SPEC.md: add "Selected Second Product Slice: Project Admin member access".
PLAN.md: add Phase 2 with docs/gate, implementation, validation, evidence tasks.
CHECKS.md: add manual checks for Project Admin member access.
HUMAN_GATE.md: add stop conditions for real auth/RBAC, DB/API, email invite, company management, access deletion.
EVIDENCE.md: add "Project Admin Member Access Document Loop" with the document pass result.
```

- [ ] **Step 5: Run document consistency checks**

Run:

```powershell
rg -n "FR-PA-00[1-9]" docs SPEC.md PLAN.md CHECKS.md HUMAN_GATE.md EVIDENCE.md
rg -n "Company|회사" docs\PRD.md docs\TRD.md docs\UI_Spec.md docs\Data_Model.md docs\Task_List.md docs\Acceptance_Criteria.md docs\Test_Scenarios.md docs\Design_Map.md docs\User_Flow.md docs\Planning_Gate_Checklist.md
```

Expected:

```text
FR-PA-001 through FR-PA-009 appear in PRD/TRD/UI/Data/Task/Acceptance/Test/Design/User_Flow/Planning docs.
Any Company/회사 matches are only in explicit out-of-scope or excluded-company statements.
```

- [ ] **Step 6: Run planning gate**

Follow `.agents/skills/planning-gate/SKILL.md`.

Expected gate result:

```text
PASS for Project Admin member access local mock slice.
No required docs missing.
No FR-to-task/acceptance/test gaps.
No company/auth/DB/API scope creep.
```

- [ ] **Step 7: Commit docs/gate**

Run:

```powershell
git add SPEC.md PLAN.md CHECKS.md HUMAN_GATE.md EVIDENCE.md docs
git commit -m "docs: plan project admin member access slice"
```

---

### Task 1: Domain Data And Helper Tests

**Files:**
- Create: `src/projectAdminData.ts`
- Create: `src/projectAdminData.test.ts`

- [ ] **Step 1: Write the failing helper tests**

Create `src/projectAdminData.test.ts`:

```ts
import { describe, expect, it } from "vitest";
import {
  availableMembersForProject,
  buildProjectAccessRows,
  initialMembers,
  initialProjectAccess,
  selectedProject
} from "./projectAdminData";

describe("project admin data helpers", () => {
  it("joins project access records to member records for the selected project", () => {
    const rows = buildProjectAccessRows(selectedProject.id, initialMembers, initialProjectAccess);

    expect(rows).toHaveLength(2);
    expect(rows.map((row) => row.email)).toEqual(["cruelkh@gmail.com", "reviewer@xd.local"]);
    expect(rows[0]).toMatchObject({
      projectId: "project-study",
      memberId: "member-owner",
      name: "개혁 이",
      role: "관리자",
      status: "활성"
    });
  });

  it("excludes members that already have access to the selected project", () => {
    const available = availableMembersForProject(selectedProject.id, initialMembers, initialProjectAccess);

    expect(available.map((member) => member.id)).toEqual(["member-field", "member-viewer"]);
  });
});
```

- [ ] **Step 2: Run helper tests and verify failure**

Run:

```powershell
npm test -- src/projectAdminData.test.ts
```

Expected: FAIL because `src/projectAdminData.ts` does not exist.

- [ ] **Step 3: Implement domain data and helpers**

Create `src/projectAdminData.ts`:

```ts
export type Project = {
  id: string;
  name: string;
};

export type MemberRole = "관리자" | "편집자" | "뷰어";
export type MemberStatus = "활성" | "대기";

export type Member = {
  id: string;
  name: string;
  email: string;
  phone: string;
};

export type ProjectMemberAccess = {
  projectId: string;
  memberId: string;
  role: MemberRole;
  status: MemberStatus;
  addedAt: string;
};

export type ProjectAccessRow = ProjectMemberAccess & Member;

export const selectedProject: Project = {
  id: "project-study",
  name: "Study_Project"
};

export const memberRoles: MemberRole[] = ["관리자", "편집자", "뷰어"];

export const initialMembers: Member[] = [
  {
    id: "member-owner",
    name: "개혁 이",
    email: "cruelkh@gmail.com",
    phone: "+82 10-4112-9638"
  },
  {
    id: "member-reviewer",
    name: "도면 검토자",
    email: "reviewer@xd.local",
    phone: "+82 10-2000-1200"
  },
  {
    id: "member-field",
    name: "현장 담당자",
    email: "field@xd.local",
    phone: "+82 10-3000-3400"
  },
  {
    id: "member-viewer",
    name: "고객 열람자",
    email: "viewer@xd.local",
    phone: "+82 10-4000-5600"
  }
];

export const initialProjectAccess: ProjectMemberAccess[] = [
  {
    projectId: "project-study",
    memberId: "member-owner",
    role: "관리자",
    status: "활성",
    addedAt: "2026.06.12."
  },
  {
    projectId: "project-study",
    memberId: "member-reviewer",
    role: "편집자",
    status: "활성",
    addedAt: "2026.06.13."
  },
  {
    projectId: "project-seaport",
    memberId: "member-field",
    role: "관리자",
    status: "활성",
    addedAt: "2026.06.14."
  }
];

export function buildProjectAccessRows(
  projectId: string,
  members: Member[],
  accessRecords: ProjectMemberAccess[]
): ProjectAccessRow[] {
  return accessRecords
    .filter((access) => access.projectId === projectId)
    .map((access) => {
      const member = members.find((candidate) => candidate.id === access.memberId);
      if (!member) {
        return undefined;
      }

      return {
        ...access,
        ...member
      };
    })
    .filter((row): row is ProjectAccessRow => Boolean(row));
}

export function availableMembersForProject(
  projectId: string,
  members: Member[],
  accessRecords: ProjectMemberAccess[]
): Member[] {
  const assignedMemberIds = new Set(
    accessRecords
      .filter((access) => access.projectId === projectId)
      .map((access) => access.memberId)
  );

  return members.filter((member) => !assignedMemberIds.has(member.id));
}

export function memberHasProjectAccess(
  projectId: string,
  memberId: string,
  accessRecords: ProjectMemberAccess[]
): boolean {
  return accessRecords.some((access) => access.projectId === projectId && access.memberId === memberId);
}
```

- [ ] **Step 4: Run helper tests and verify pass**

Run:

```powershell
npm test -- src/projectAdminData.test.ts
```

Expected: PASS, 1 test file / 2 tests.

- [ ] **Step 5: Commit data helpers**

Run:

```powershell
git add src/projectAdminData.ts src/projectAdminData.test.ts
git commit -m "feat: add project admin member access data"
```

---

### Task 2: Project Admin View Rendering

**Files:**
- Create: `src/ProjectAdminView.tsx`
- Create: `src/ProjectAdminView.test.tsx`
- Modify: `src/styles.css`

- [ ] **Step 1: Write failing render tests**

Create `src/ProjectAdminView.test.tsx`:

```ts
import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import ProjectAdminView from "./ProjectAdminView";

function renderProjectAdmin() {
  return {
    user: userEvent.setup(),
    ...render(<ProjectAdminView onBackToProjects={() => undefined} />)
  };
}

function accessRows() {
  return screen.getAllByTestId("project-access-row");
}

describe("ProjectAdminView", () => {
  it("renders the Project Admin member access shell for Study_Project", () => {
    renderProjectAdmin();

    expect(screen.getByText("Project Admin")).toBeInTheDocument();
    expect(screen.getByText("Study_Project")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "구성원" })).toHaveAttribute("aria-current", "page");
    expect(screen.getByRole("heading", { name: "구성원" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "구성원 추가" })).toBeInTheDocument();
    expect(screen.getByPlaceholderText("이름 또는 이메일로 구성원 검색...")).toBeInTheDocument();

    ["이름", "이메일", "전화", "상태", "역할", "추가된 일시"].forEach((column) => {
      expect(screen.getByRole("columnheader", { name: column })).toBeInTheDocument();
    });

    expect(accessRows()).toHaveLength(2);
    expect(screen.getByText("개혁 이")).toBeInTheDocument();
    expect(screen.getByText("도면 검토자")).toBeInTheDocument();
    expect(screen.queryByText("현장 담당자")).not.toBeInTheDocument();
  });

  it("shows the selected member in the right inspector", () => {
    renderProjectAdmin();

    const inspector = screen.getByRole("complementary", { name: "구성원 상세" });
    expect(within(inspector).getByText("개혁 이")).toBeInTheDocument();
    expect(within(inspector).getByText("cruelkh@gmail.com")).toBeInTheDocument();
    expect(within(inspector).getByDisplayValue("관리자")).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run render tests and verify failure**

Run:

```powershell
npm test -- src/ProjectAdminView.test.tsx
```

Expected: FAIL because `src/ProjectAdminView.tsx` does not exist.

- [ ] **Step 3: Implement minimal ProjectAdminView shell**

Create `src/ProjectAdminView.tsx`:

```tsx
import { ArrowLeft, Download, Filter, Search, Settings, Users, X } from "lucide-react";
import { FormEvent, useMemo, useState } from "react";
import {
  buildProjectAccessRows,
  initialMembers,
  initialProjectAccess,
  memberRoles,
  ProjectAccessRow,
  ProjectMemberAccess,
  selectedProject
} from "./projectAdminData";

type ProjectAdminViewProps = {
  onBackToProjects: () => void;
};

type AddMemberForm = {
  memberId: string;
  role: ProjectMemberAccess["role"];
};

const emptyAddMemberForm: AddMemberForm = {
  memberId: "",
  role: "뷰어"
};

export default function ProjectAdminView({ onBackToProjects }: ProjectAdminViewProps) {
  const [accessRecords, setAccessRecords] = useState<ProjectMemberAccess[]>(initialProjectAccess);
  const [query, setQuery] = useState("");
  const [selectedMemberId, setSelectedMemberId] = useState("member-owner");
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [addForm, setAddForm] = useState<AddMemberForm>(emptyAddMemberForm);
  const [addError, setAddError] = useState("");

  const accessRows = useMemo(() => {
    return buildProjectAccessRows(selectedProject.id, initialMembers, accessRecords);
  }, [accessRecords]);

  const filteredRows = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    if (!normalized) {
      return accessRows;
    }

    return accessRows.filter((row) => {
      return row.name.toLowerCase().includes(normalized) || row.email.toLowerCase().includes(normalized);
    });
  }, [accessRows, query]);

  const selectedRow = accessRows.find((row) => row.memberId === selectedMemberId) ?? accessRows[0];

  function openAddModal() {
    setAddForm(emptyAddMemberForm);
    setAddError("");
    setIsAddModalOpen(true);
  }

  function closeAddModal() {
    setAddForm(emptyAddMemberForm);
    setAddError("");
    setIsAddModalOpen(false);
  }

  function submitAddMember(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setAddError("구성원을 선택하세요.");
  }

  return (
    <main className="admin-shell">
      <aside className="admin-rail" aria-label="Project Admin 메뉴">
        <div className="admin-product">
          <Settings size={18} />
          <span>Project Admin</span>
        </div>
        {["구성원", "회사", "브리지", "액티비티", "알림", "위치", "설정"].map((item) => (
          <button key={item} type="button" aria-current={item === "구성원" ? "page" : undefined}>
            <Users size={17} aria-hidden="true" />
            <span>{item}</span>
          </button>
        ))}
      </aside>

      <section className="admin-main">
        <header className="admin-topline">
          <button className="ghost-action" type="button" onClick={onBackToProjects}>
            <ArrowLeft size={16} />
            프로젝트 목록
          </button>
          <strong>{selectedProject.name}</strong>
        </header>

        <section className="admin-panel" aria-labelledby="member-access-title">
          <div className="admin-heading">
            <h1 id="member-access-title">구성원</h1>
            <button className="primary-action" type="button" onClick={openAddModal}>
              구성원 추가
            </button>
          </div>

          <div className="admin-tools">
            <button className="secondary-action" type="button">
              <Download size={16} />
              내보내기
            </button>
            <label className="search-field admin-search">
              <Search size={18} aria-hidden="true" />
              <input
                aria-label="구성원 검색"
                placeholder="이름 또는 이메일로 구성원 검색..."
                value={query}
                onChange={(event) => setQuery(event.target.value)}
              />
            </label>
            <button className="icon-button" type="button" aria-label="필터">
              <Filter size={18} />
            </button>
          </div>

          <div className="table-scroll admin-table-scroll">
            <table className="project-table admin-member-table">
              <thead>
                <tr>
                  <th scope="col">이름</th>
                  <th scope="col">이메일</th>
                  <th scope="col">전화</th>
                  <th scope="col">상태</th>
                  <th scope="col">역할</th>
                  <th scope="col">추가된 일시</th>
                  <th scope="col" aria-label="설정">
                    <Settings size={18} />
                  </th>
                </tr>
              </thead>
              <tbody>
                {filteredRows.map((row) => (
                  <tr
                    key={row.memberId}
                    data-testid="project-access-row"
                    className={row.memberId === selectedRow?.memberId ? "selected-row" : undefined}
                    onClick={() => setSelectedMemberId(row.memberId)}
                  >
                    <td>{row.name}</td>
                    <td>{row.email}</td>
                    <td>{row.phone}</td>
                    <td>{row.status}</td>
                    <td>{row.role}</td>
                    <td>{row.addedAt}</td>
                    <td />
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </section>

      <MemberInspector row={selectedRow} />

      {isAddModalOpen ? (
        <AddMemberModal
          form={addForm}
          error={addError}
          onClose={closeAddModal}
          onSubmit={submitAddMember}
          onUpdate={setAddForm}
        />
      ) : null}
    </main>
  );
}

function MemberInspector({ row }: { row: ProjectAccessRow | undefined }) {
  if (!row) {
    return (
      <aside className="admin-inspector" role="complementary" aria-label="구성원 상세">
        <p>선택된 구성원이 없습니다.</p>
      </aside>
    );
  }

  return (
    <aside className="admin-inspector" role="complementary" aria-label="구성원 상세">
      <div className="member-avatar" aria-hidden="true">
        {row.name.slice(0, 1)}
      </div>
      <h2>{row.name}</h2>
      <a href={`mailto:${row.email}`}>{row.email}</a>
      <p>{row.phone}</p>
      <span className="status-pill">{row.status}</span>
      <label className="field select-field">
        <span>역할</span>
        <select value={row.role} readOnly>
          {memberRoles.map((role) => (
            <option key={role}>{role}</option>
          ))}
        </select>
      </label>
    </aside>
  );
}

type AddMemberModalProps = {
  form: AddMemberForm;
  error: string;
  onClose: () => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  onUpdate: (form: AddMemberForm) => void;
};

function AddMemberModal({ form, error, onClose, onSubmit, onUpdate }: AddMemberModalProps) {
  return (
    <div className="modal-backdrop">
      <form className="project-modal member-modal" role="dialog" aria-modal="true" aria-labelledby="add-member-title" onSubmit={onSubmit}>
        <header className="modal-header">
          <h2 id="add-member-title">구성원 추가</h2>
          <button className="modal-close" type="button" aria-label="닫기" onClick={onClose}>
            <X size={22} />
          </button>
        </header>
        <div className="modal-body">
          <label className="field select-field">
            <span>구성원</span>
            <select value={form.memberId} onChange={(event) => onUpdate({ ...form, memberId: event.target.value })}>
              <option value="">구성원 선택</option>
              {initialMembers.map((member) => (
                <option key={member.id} value={member.id}>
                  {member.name} / {member.email}
                </option>
              ))}
            </select>
          </label>
          <label className="field select-field">
            <span>역할</span>
            <select value={form.role} onChange={(event) => onUpdate({ ...form, role: event.target.value as ProjectMemberAccess["role"] })}>
              {memberRoles.map((role) => (
                <option key={role}>{role}</option>
              ))}
            </select>
          </label>
          {error ? <p className="field-error">{error}</p> : null}
        </div>
        <footer className="modal-footer">
          <button className="secondary-action" type="button" onClick={onClose}>
            취소
          </button>
          <button className="primary-action" type="submit">
            추가
          </button>
        </footer>
      </form>
    </div>
  );
}
```

- [ ] **Step 4: Add minimal styles**

Append to `src/styles.css`:

```css
.admin-shell {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 220px minmax(0, 1fr) 360px;
  background: #f7f9fb;
}

.admin-rail {
  background: #eef3f7;
  border-right: 1px solid #d9e1e8;
  padding: 16px 10px;
}

.admin-product,
.admin-rail button {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 10px;
  min-height: 38px;
  border: 0;
  background: transparent;
  color: #26384a;
  font-weight: 600;
  text-align: left;
}

.admin-rail button[aria-current="page"] {
  color: #1476b8;
  background: #dfeffc;
}

.admin-main {
  min-width: 0;
  padding: 24px;
}

.admin-topline,
.admin-heading,
.admin-tools {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.admin-panel {
  margin-top: 24px;
}

.admin-heading h1 {
  margin: 0;
  font-size: 28px;
}

.admin-tools {
  justify-content: flex-end;
  margin: 22px 0 14px;
}

.admin-search {
  min-width: 320px;
}

.admin-table-scroll {
  background: #ffffff;
}

.admin-member-table tr {
  cursor: pointer;
}

.selected-row {
  background: #edf8ff;
}

.admin-inspector {
  background: #ffffff;
  border-left: 1px solid #d9e1e8;
  padding: 28px;
}

.member-avatar {
  width: 58px;
  height: 58px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  background: #d8e0eb;
  color: #3d4c5f;
  font-weight: 700;
  margin-bottom: 12px;
}

.admin-inspector h2 {
  margin: 0 0 6px;
  font-size: 18px;
}

.status-pill {
  display: inline-flex;
  margin: 12px 0 18px;
  padding: 4px 10px;
  border-radius: 999px;
  background: #dff2e2;
  color: #2e7d3c;
  font-weight: 700;
  font-size: 12px;
}

.member-modal {
  max-width: 520px;
}

@media (max-width: 980px) {
  .admin-shell {
    grid-template-columns: 76px minmax(0, 1fr);
  }

  .admin-rail span,
  .admin-product span {
    display: none;
  }

  .admin-inspector {
    grid-column: 1 / -1;
    border-left: 0;
    border-top: 1px solid #d9e1e8;
  }

  .admin-tools {
    align-items: stretch;
    flex-direction: column;
  }

  .admin-search {
    min-width: 0;
  }
}
```

- [ ] **Step 5: Run render tests and verify pass**

Run:

```powershell
npm test -- src/ProjectAdminView.test.tsx
```

Expected: PASS, 1 test file / 2 tests.

---

### Task 3: Search And Row Selection Behavior

**Files:**
- Modify: `src/ProjectAdminView.test.tsx`
- Modify: `src/ProjectAdminView.tsx`

- [ ] **Step 1: Add failing interaction tests**

Append inside the existing `describe("ProjectAdminView", ...)` block in `src/ProjectAdminView.test.tsx`:

```ts
  it("filters project access members by name or email and restores all rows when cleared", async () => {
    const { user } = renderProjectAdmin();
    const search = screen.getByPlaceholderText("이름 또는 이메일로 구성원 검색...");

    await user.type(search, "검토");
    expect(accessRows()).toHaveLength(1);
    expect(screen.getByText("도면 검토자")).toBeInTheDocument();
    expect(screen.queryByText("개혁 이")).not.toBeInTheDocument();

    await user.clear(search);
    await user.type(search, "cruelkh");
    expect(accessRows()).toHaveLength(1);
    expect(screen.getByText("개혁 이")).toBeInTheDocument();

    await user.clear(search);
    expect(accessRows()).toHaveLength(2);
  });

  it("updates the right inspector when a member row is selected", async () => {
    const { user } = renderProjectAdmin();

    await user.click(screen.getByText("도면 검토자"));

    const inspector = screen.getByRole("complementary", { name: "구성원 상세" });
    expect(within(inspector).getByText("도면 검토자")).toBeInTheDocument();
    expect(within(inspector).getByText("reviewer@xd.local")).toBeInTheDocument();
    expect(within(inspector).getByDisplayValue("편집자")).toBeInTheDocument();
  });
```

- [ ] **Step 2: Run interaction tests**

Run:

```powershell
npm test -- src/ProjectAdminView.test.tsx
```

Expected: PASS if Task 2 implementation already included search and row selection. If FAIL, update `ProjectAdminView.tsx` so:

```tsx
const filteredRows = useMemo(() => {
  const normalized = query.trim().toLowerCase();
  if (!normalized) {
    return accessRows;
  }

  return accessRows.filter((row) => {
    return row.name.toLowerCase().includes(normalized) || row.email.toLowerCase().includes(normalized);
  });
}, [accessRows, query]);
```

and each row has:

```tsx
onClick={() => setSelectedMemberId(row.memberId)}
```

- [ ] **Step 3: Commit search/selection**

Run:

```powershell
git add src/ProjectAdminView.tsx src/ProjectAdminView.test.tsx
git commit -m "feat: add project admin member search and selection"
```

---

### Task 4: Add Existing Member Modal

**Files:**
- Modify: `src/ProjectAdminView.test.tsx`
- Modify: `src/ProjectAdminView.tsx`

- [ ] **Step 1: Add failing add-member tests**

Append inside the existing `describe("ProjectAdminView", ...)` block:

```ts
  it("opens add-member modal and blocks empty submit", async () => {
    const { user } = renderProjectAdmin();

    await user.click(screen.getByRole("button", { name: "구성원 추가" }));
    expect(screen.getByRole("dialog", { name: "구성원 추가" })).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "추가" }));
    expect(screen.getByText("구성원을 선택하세요.")).toBeInTheDocument();
    expect(accessRows()).toHaveLength(2);
  });

  it("blocks duplicate project-member access", async () => {
    const { user } = renderProjectAdmin();

    await user.click(screen.getByRole("button", { name: "구성원 추가" }));
    await user.selectOptions(screen.getByLabelText("구성원"), "member-owner");
    await user.click(screen.getByRole("button", { name: "추가" }));

    expect(screen.getByText("이미 이 프로젝트에 추가된 구성원입니다.")).toBeInTheDocument();
    expect(accessRows()).toHaveLength(2);
  });

  it("adds an existing mock member with a selected project role", async () => {
    const { user } = renderProjectAdmin();

    await user.click(screen.getByRole("button", { name: "구성원 추가" }));
    await user.selectOptions(screen.getByLabelText("구성원"), "member-field");
    await user.selectOptions(screen.getByLabelText("역할"), "뷰어");
    await user.click(screen.getByRole("button", { name: "추가" }));

    expect(screen.queryByRole("dialog", { name: "구성원 추가" })).not.toBeInTheDocument();
    expect(accessRows()).toHaveLength(3);
    expect(screen.getByText("현장 담당자")).toBeInTheDocument();

    await user.click(screen.getByText("현장 담당자"));
    const inspector = screen.getByRole("complementary", { name: "구성원 상세" });
    expect(within(inspector).getByText("field@xd.local")).toBeInTheDocument();
    expect(within(inspector).getByDisplayValue("뷰어")).toBeInTheDocument();
  });
```

- [ ] **Step 2: Run add-member tests and verify failure**

Run:

```powershell
npm test -- src/ProjectAdminView.test.tsx
```

Expected: FAIL if Task 2 still uses the placeholder `submitAddMember` implementation.

- [ ] **Step 3: Implement add-member behavior**

In `src/ProjectAdminView.tsx`, update imports:

```tsx
import {
  availableMembersForProject,
  buildProjectAccessRows,
  initialMembers,
  initialProjectAccess,
  memberHasProjectAccess,
  memberRoles,
  ProjectAccessRow,
  ProjectMemberAccess,
  selectedProject
} from "./projectAdminData";
```

Add available member derivation:

```tsx
const availableMembers = useMemo(() => {
  return availableMembersForProject(selectedProject.id, initialMembers, accessRecords);
}, [accessRecords]);
```

Replace `submitAddMember`:

```tsx
function submitAddMember(event: FormEvent<HTMLFormElement>) {
  event.preventDefault();

  if (!addForm.memberId) {
    setAddError("구성원을 선택하세요.");
    return;
  }

  if (memberHasProjectAccess(selectedProject.id, addForm.memberId, accessRecords)) {
    setAddError("이미 이 프로젝트에 추가된 구성원입니다.");
    return;
  }

  const nextAccess: ProjectMemberAccess = {
    projectId: selectedProject.id,
    memberId: addForm.memberId,
    role: addForm.role,
    status: "활성",
    addedAt: "방금 전"
  };

  setAccessRecords((current) => [...current, nextAccess]);
  setSelectedMemberId(addForm.memberId);
  closeAddModal();
}
```

Pass `availableMembers` into `AddMemberModal`:

```tsx
<AddMemberModal
  form={addForm}
  availableMembers={availableMembers}
  error={addError}
  onClose={closeAddModal}
  onSubmit={submitAddMember}
  onUpdate={setAddForm}
/>
```

Update `AddMemberModalProps`:

```tsx
type AddMemberModalProps = {
  form: AddMemberForm;
  availableMembers: typeof initialMembers;
  error: string;
  onClose: () => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  onUpdate: (form: AddMemberForm) => void;
};
```

Update modal signature:

```tsx
function AddMemberModal({ form, availableMembers, error, onClose, onSubmit, onUpdate }: AddMemberModalProps) {
```

Render all members but disable already-added options so duplicate behavior can still be tested:

```tsx
{initialMembers.map((member) => {
  const isAvailable = availableMembers.some((candidate) => candidate.id === member.id);

  return (
    <option key={member.id} value={member.id} disabled={!isAvailable}>
      {member.name} / {member.email}
    </option>
  );
})}
```

If disabled options prevent the duplicate test from selecting `member-owner`, do not disable options. Instead show all members and rely on submit validation. The duplicate test is the source of truth.

- [ ] **Step 4: Run add-member tests and verify pass**

Run:

```powershell
npm test -- src/ProjectAdminView.test.tsx
```

Expected: PASS.

- [ ] **Step 5: Commit add-member modal behavior**

Run:

```powershell
git add src/ProjectAdminView.tsx src/ProjectAdminView.test.tsx
git commit -m "feat: add project member access modal"
```

---

### Task 5: App Integration

**Files:**
- Modify: `src/App.tsx`
- Modify: `src/App.test.tsx`
- Modify: `src/styles.css`

- [ ] **Step 1: Add failing app integration test**

Append to `src/App.test.tsx` inside the existing `describe("initial setup project list and create modal", ...)` block:

```ts
  it("opens Project Admin member access for Study_Project from the project list", async () => {
    const { user } = renderApp();

    await user.click(screen.getByRole("button", { name: "Study_Project Project Admin 열기" }));

    expect(screen.getByText("Project Admin")).toBeInTheDocument();
    expect(screen.getByText("Study_Project")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "구성원" })).toBeInTheDocument();
    expect(screen.getByText("개혁 이")).toBeInTheDocument();
  });
```

- [ ] **Step 2: Run integration test and verify failure**

Run:

```powershell
npm test -- src/App.test.tsx
```

Expected: FAIL because the project list has no Project Admin entry action.

- [ ] **Step 3: Wire App mode**

In `src/App.tsx`, add import:

```tsx
import ProjectAdminView from "./ProjectAdminView";
```

Add state near existing state:

```tsx
const [activeView, setActiveView] = useState<"projects" | "project-admin">("projects");
```

Before the current `return`, add:

```tsx
if (activeView === "project-admin") {
  return <ProjectAdminView onBackToProjects={() => setActiveView("projects")} />;
}
```

Inside the `Study_Project` row name cell, add a scoped action after the name:

```tsx
{project.id === "project-study" ? (
  <button
    className="inline-link-action"
    type="button"
    aria-label={`${project.name} Project Admin 열기`}
    onClick={() => setActiveView("project-admin")}
  >
    Project Admin
  </button>
) : null}
```

- [ ] **Step 4: Add inline action style**

Append to `src/styles.css`:

```css
.inline-link-action {
  width: fit-content;
  border: 0;
  padding: 0;
  background: transparent;
  color: #1476b8;
  font: inherit;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
}

.inline-link-action:hover {
  text-decoration: underline;
}
```

- [ ] **Step 5: Run app integration test and verify pass**

Run:

```powershell
npm test -- src/App.test.tsx
```

Expected: PASS.

- [ ] **Step 6: Run full automated tests**

Run:

```powershell
npm test
npm run build
```

Expected:

```text
npm test: PASS, all test files pass.
npm run build: PASS, tsc && vite build completes.
```

- [ ] **Step 7: Commit app integration**

Run:

```powershell
git add src/App.tsx src/App.test.tsx src/styles.css
git commit -m "feat: open project admin from project list"
```

---

### Task 6: Validator Loop, Evidence, And Handoff

**Files:**
- Modify: `CHECKS.md`
- Modify: `EVIDENCE.md`
- Modify: `docs/sessions/NEXT_SESSION.md`
- Optionally modify: `PLAN.md`

- [ ] **Step 1: Update manual checks**

Add to `CHECKS.md`:

```markdown
## Manual Checks For Project Admin Member Access

Reference screenshots:

- `reference/acc-screenshots/ScreenShot Tool -20260612102437.png`
- `reference/acc-screenshots/Video Screen1781227558018.png`

Pass/fail checks:

- Project list exposes a local path to open Project Admin for `Study_Project`.
- Project Admin shows `구성원` selected in the left rail.
- Member table shows only current `Study_Project` access rows before adding a new member.
- Search filters by member name and email and clears back to all rows.
- Selecting a row updates the right inspector.
- `구성원 추가` modal opens.
- Empty add submit shows `구성원을 선택하세요.`
- Duplicate access submit shows `이미 이 프로젝트에 추가된 구성원입니다.`
- Valid existing member + role submit adds one row and closes the modal.
- Company information is not shown in the slice.
- Browser console has no errors during open, search, select, add, duplicate validation, cancel, and close flows.
- Desktop and narrow widths do not show overlapping text, clipped button labels, or broken modal layout.
```

- [ ] **Step 2: Run validator commands**

Run:

```powershell
npm test
npm run build
npm run dev -- --port 5173
```

Expected:

```text
npm test: PASS
npm run build: PASS
dev server starts at http://127.0.0.1:5173/
```

- [ ] **Step 3: Browser validation**

Open `http://127.0.0.1:5173/` and validate:

```text
Desktop: project list -> Project Admin -> search -> select -> add modal -> empty validation -> duplicate validation -> valid add.
Narrow/mobile: table scroll, inspector, modal fit.
Console: no errors.
```

Save screenshots:

```text
docs/evidence/project-admin-desktop.png
docs/evidence/project-admin-add-member-modal.png
docs/evidence/project-admin-mobile.png
```

- [ ] **Step 4: Update evidence**

Add to `EVIDENCE.md`:

```markdown
## Project Admin Member Access Implementation

```text
Date: 2026-06-17
Scope:
  Project Admin - 프로젝트 접근 구성원 관리

Implemented:
  Project, Member, and ProjectMemberAccess local mock model.
  Project Admin member access table for Study_Project.
  Search by member name/email.
  Row selection and right inspector.
  Add existing member modal.
  Empty and duplicate validation.
  Company information excluded.

Verification:
  npm test: PASS
  npm run build: PASS
  Browser desktop: PASS
  Browser narrow/mobile: PASS
  Console errors: none observed

Evidence files:
  docs/evidence/project-admin-desktop.png
  docs/evidence/project-admin-add-member-modal.png
  docs/evidence/project-admin-mobile.png

Human gate:
  No real auth/RBAC enforcement, DB/API persistence, email invite, company management, deletion, or Autodesk cloud/API integration introduced.
```
```

- [ ] **Step 5: Update handoff**

Update `docs/sessions/NEXT_SESSION.md`:

```markdown
## Immediate Resume - Project Admin Member Access

The Project Admin member access slice is implemented and verified.

Current completed product slices:

1. Initial setup project list and project creation modal.
2. Project Admin member access for `Study_Project`.

Next recommended slice:

1. Build shell + Sheets list.
2. Or Project Admin role/permission matrix only after human approval, because real RBAC remains gated.
```

- [ ] **Step 6: Commit evidence and handoff**

Run:

```powershell
git add CHECKS.md EVIDENCE.md docs/sessions/NEXT_SESSION.md PLAN.md docs/evidence
git commit -m "docs: record project admin member access evidence"
```

- [ ] **Step 7: Final clean-state verification**

Run:

```powershell
git status --short --untracked-files=all
npm test
npm run build
```

Expected:

```text
git status: clean
npm test: PASS
npm run build: PASS
```

---

## Self-Review Checklist

- Spec coverage:
  - Project and Member peer-level model: Task 1.
  - ProjectMemberAccess relation: Task 1 and Task 4.
  - Current project context `Study_Project`: Task 2 and Task 5.
  - Member access table: Task 2.
  - Search: Task 3.
  - Row selection and inspector: Task 2 and Task 3.
  - Add existing member modal: Task 4.
  - Duplicate validation: Task 4.
  - Company/auth/DB/API exclusion: Task 0 and Task 6.

- Placeholder scan:
  - No forbidden placeholder steps are intentionally used.

- Type consistency:
  - `Project`, `Member`, `ProjectMemberAccess`, `ProjectAccessRow`, `MemberRole`, and `MemberStatus` are introduced in Task 1 and reused consistently afterward.
