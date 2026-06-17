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
