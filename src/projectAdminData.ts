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
