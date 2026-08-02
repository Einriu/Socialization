import { describe, expect, it } from "vitest";
import { parseSse, type SseEvent } from "@/utils/sse";

function responseWith(text: string): Response {
  const stream = new ReadableStream<Uint8Array>({
    start(controller) {
      controller.enqueue(new TextEncoder().encode(text));
      controller.close();
    },
  });
  return new Response(stream);
}

describe("parseSse", () => {
  it("解析多个 data 事件", async () => {
    const events: SseEvent[] = [];
    for await (const event of parseSse(
      responseWith('data: {"type": "delta", "content": "你好"}\n\ndata: {"type": "done"}\n\n'),
    )) {
      events.push(event);
    }
    expect(events).toHaveLength(2);
    expect(events[0]).toEqual({ type: "delta", content: "你好" });
    expect(events[1]).toEqual({ type: "done" });
  });

  it("忽略无法解析的行", async () => {
    const events: SseEvent[] = [];
    for await (const event of parseSse(responseWith('data: not-json\n\ndata: {"type": "ok"}\n\n'))) {
      events.push(event);
    }
    expect(events).toHaveLength(1);
    expect(events[0]?.type).toBe("ok");
  });
});
