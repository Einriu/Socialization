export interface SseEvent {
  type: string;
  [key: string]: unknown;
}

export async function* parseSse(response: Response): AsyncGenerator<SseEvent> {
  if (!response.body) {
    throw new Error("当前环境不支持流式响应");
  }
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      break;
    }
    buffer += decoder.decode(value, { stream: true });
    let index = buffer.indexOf("\n\n");
    while (index !== -1) {
      const raw = buffer.slice(0, index);
      buffer = buffer.slice(index + 2);
      for (const line of raw.split("\n")) {
        if (line.startsWith("data: ")) {
          try {
            yield JSON.parse(line.slice(6)) as SseEvent;
          } catch {
            // 忽略无法解析的行
          }
        }
      }
      index = buffer.indexOf("\n\n");
    }
  }
}
