import { describe, it, expect, vi, afterEach } from "vitest";
import { fetchGraph, fetchNeighbors, confirmEdge, rejectEdge } from "./kg";

afterEach(() => vi.restoreAllMocks());

describe("kg api", () => {
  it("fetchGraph 는 project_name 쿼리로 /api/kg/graph 를 부른다", async () => {
    const spy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ nodes: [{ id: "eq:E1" }], edges: [] }), { status: 200 }));
    const g = await fetchGraph("P1");
    expect(spy.mock.calls[0][0]).toContain("/api/kg/graph?project_name=P1");
    expect(g.nodes[0].id).toBe("eq:E1");
  });

  it("fetchNeighbors 는 id·depth 를 넘긴다", async () => {
    const spy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ found: true, nodes: [], edges: [] }), { status: 200 }));
    await fetchNeighbors("P1", "eq:E1", 2);
    const url = spy.mock.calls[0][0] as string;
    expect(url).toContain("id=eq%3AE1");
    expect(url).toContain("depth=2");
  });
});

describe("kg writeback api", () => {
  it("confirmEdge 는 /api/kg/edge/confirm 로 project/src/dst 를 POST 한다", async () => {
    const spy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ ok: true, edge_key: "eq:E1|eq:E2|relates_to", new_track: "curated" }),
        { status: 200 }));
    const out = await confirmEdge("P1", "eq:E1", "eq:E2");
    const [url, init] = spy.mock.calls[0];
    expect(String(url)).toContain("/api/kg/edge/confirm");
    expect(init?.method).toBe("POST");
    expect(JSON.parse(String(init?.body))).toEqual({ project_name: "P1", src: "eq:E1", dst: "eq:E2" });
    expect(out.new_track).toBe("curated");
  });

  it("rejectEdge 는 reason 을 body 에 실어 POST 하고 hidden 을 돌려준다", async () => {
    const spy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ ok: true, edge_key: "eq:E2|eq:E3|relates_to", hidden: true }),
        { status: 200 }));
    const out = await rejectEdge("P1", "eq:E2", "eq:E3", "오탐");
    const [url, init] = spy.mock.calls[0];
    expect(String(url)).toContain("/api/kg/edge/reject");
    expect(JSON.parse(String(init?.body)).reason).toBe("오탐");
    expect(out.hidden).toBe(true);
  });

  it("실패 응답은 throw 한다", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response("bad", { status: 400 }));
    await expect(confirmEdge("P1", "eq:E1", "sh:s1")).rejects.toThrow();
  });
});
