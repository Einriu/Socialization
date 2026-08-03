import { useEffect, useState, type FormEvent } from "react";
import {
  evaluateSession,
  listPracticeMessages,
  listPracticeSessions,
  practiceSendStream,
  type PracticeMessageItem,
  type PracticeSessionInfo,
} from "@/api/p2";
import { Button } from "@/components/ui/button";
import { ErrorText, TextArea } from "@/components/ui/field";
import { matchRoute, useRouter } from "@/lib/router";
import { parseSse } from "@/utils/sse";

const CHANNEL_LABELS: Record<string, string> = {
  online: "线上（微信等）",
  offline: "线下社交",
};

export function PracticeSessionPage() {
  const { path, navigate } = useRouter();
  const match = matchRoute(path, "/practice/session/:id");
  const routeId = match?.params.id ?? null;

  const [sessions, setSessions] = useState<PracticeSessionInfo[]>([]);
  const [currentId, setCurrentId] = useState<string | null>(null);
  const [sessionInfo, setSessionInfo] = useState<PracticeSessionInfo | null>(null);
  const [messages, setMessages] = useState<PracticeMessageItem[]>([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [evaluation, setEvaluation] = useState<{
    scores: Record<string, number>;
    summary: string;
  } | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      try {
        const items = await listPracticeSessions();
        if (cancelled) {
          return;
        }
        setSessions(items);
        const target = routeId ?? items[0]?.id ?? null;
        if (!target) {
          return;
        }
        const info = items.find((item) => item.id === target) ?? null;
        const msgs = await listPracticeMessages(target);
        if (cancelled) {
          return;
        }
        setCurrentId(target);
        setSessionInfo(info);
        setMessages(msgs);
      } catch (e) {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : "加载失败");
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [routeId]);

  const openSession = async (id: string) => {
    setEvaluation(null);
    setError(null);
    setCurrentId(id);
    setSessionInfo(sessions.find((item) => item.id === id) ?? null);
    try {
      setMessages(await listPracticeMessages(id));
    } catch (e) {
      setError(e instanceof Error ? e.message : "加载消息失败");
    }
  };

  const send = async (e: FormEvent) => {
    e.preventDefault();
    if (!currentId || !input.trim() || streaming) {
      return;
    }
    const userMessage: PracticeMessageItem = {
      id: `local-${Date.now()}`,
      role: "user",
      content: input.trim(),
    };
    const assistantMessage: PracticeMessageItem = {
      id: `local-ai-${Date.now()}`,
      role: "assistant",
      content: "",
    };
    setMessages((prev) => [...prev, userMessage, assistantMessage]);
    setInput("");
    setStreaming(true);
    try {
      const response = await practiceSendStream(currentId, userMessage.content);
      for await (const event of parseSse(response)) {
        if (event.type === "delta") {
          setMessages((prev) =>
            prev.map((item) =>
              item.id === assistantMessage.id
                ? { ...item, content: item.content + String(event.content ?? "") }
                : item,
            ),
          );
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "发送失败");
    } finally {
      setStreaming(false);
    }
  };

  const evaluate = async () => {
    if (!currentId) {
      return;
    }
    try {
      setEvaluation(await evaluateSession(currentId));
      setSessions(await listPracticeSessions());
    } catch (e) {
      setError(e instanceof Error ? e.message : "评分失败");
    }
  };

  return (
    <main className="mx-auto w-full max-w-5xl space-y-6 px-6 py-10">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold tracking-tight">练习会话</h1>
        <Button variant="outline" size="sm" onClick={() => navigate("/practice")}>
          新建场景
        </Button>
      </div>
      <ErrorText message={error} />

      {!currentId ? (
        <div className="space-y-3 rounded-lg border bg-card p-10 text-center">
          <p className="text-sm text-muted-foreground">还没有练习会话，先去创建场景并生成社交背景。</p>
          <Button onClick={() => navigate("/practice")}>去创建场景</Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-[240px_1fr]">
          <aside className="space-y-1">
            <h2 className="text-sm font-medium text-muted-foreground">历史会话</h2>
            {sessions.map((session) => (
              <button
                key={session.id}
                type="button"
                onClick={() => void openSession(session.id)}
                className={`block w-full truncate rounded px-2 py-1.5 text-left text-sm ${
                  currentId === session.id
                    ? "bg-secondary font-medium"
                    : "hover:bg-accent"
                }`}
              >
                {session.title}
                {session.status === "completed" ? "（已完成）" : ""}
              </button>
            ))}
          </aside>

          <section className="space-y-3">
            {sessionInfo && (
              <div className="space-y-1 rounded-lg border bg-card p-3 text-sm text-muted-foreground">
                <p>
                  渠道：{CHANNEL_LABELS[sessionInfo.channel] ?? sessionInfo.channel}
                  {sessionInfo.tags.length > 0 && <> · 标签：{sessionInfo.tags.join("、")}</>}
                </p>
                {sessionInfo.participants.length > 0 && (
                  <p>在场角色：{sessionInfo.participants.map((p) => p.name).join("、")}</p>
                )}
                {sessionInfo.custom_prompt && (
                  <details>
                    <summary className="cursor-pointer">查看场景背景</summary>
                    <p className="mt-1 whitespace-pre-wrap rounded bg-background p-2">
                      {sessionInfo.custom_prompt}
                    </p>
                  </details>
                )}
              </div>
            )}

            <div className="space-y-3 rounded-lg border bg-card p-4">
              {messages.length === 0 && (
                <p className="text-center text-sm text-muted-foreground">
                  开始练习后与 AI 角色对话，角色之间也会互相交流
                </p>
              )}
              {messages.flatMap((message) => renderBubbles(message))}
            </div>

            <form onSubmit={(e) => void send(e)} className="flex gap-2">
              <TextArea
                className="min-h-16"
                placeholder="输入你的回应，也可以暂时旁观角色们聊天…"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                disabled={streaming || !currentId}
              />
              <Button type="submit" disabled={streaming || !input.trim()}>
                {streaming ? "对话中…" : "发送"}
              </Button>
            </form>

            {currentId && !streaming && (
              <Button variant="outline" onClick={() => void evaluate()}>
                结束并评分
              </Button>
            )}
            {evaluation && (
              <div className="space-y-2 rounded-lg border bg-card p-4">
                <h3 className="font-medium">评分</h3>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(evaluation.scores).map(([key, value]) => (
                    <span key={key} className="rounded bg-secondary px-2 py-1 text-sm">
                      {key}：{value}
                    </span>
                  ))}
                </div>
                {evaluation.summary && (
                  <p className="text-sm text-muted-foreground">{evaluation.summary}</p>
                )}
              </div>
            )}
          </section>
        </div>
      )}
    </main>
  );
}

function renderBubbles(message: PracticeMessageItem): React.ReactNode[] {
  if (message.role === "user") {
    return [
      <div key={message.id} className="flex justify-end">
        <div className="max-w-[80%] whitespace-pre-wrap rounded-lg border bg-primary px-3 py-2 text-sm text-primary-foreground">
          {message.content}
        </div>
      </div>,
    ];
  }
  const segments = splitBySpeaker(message.content);
  return segments.map((segment, index) => (
    <div key={`${message.id}-${index}`} className="flex justify-start">
      <div className="max-w-[80%] whitespace-pre-wrap rounded-lg border bg-background px-3 py-2 text-sm">
        {segment.speaker && (
          <span className="mr-1 text-xs font-medium text-primary">{segment.speaker}</span>
        )}
        {segment.text}
      </div>
    </div>
  ));
}

function splitBySpeaker(content: string): { speaker?: string; text: string }[] {
  const segments: { speaker?: string; text: string }[] = [];
  let current: { speaker?: string; text: string[] } = { text: [] };
  for (const line of content.split("\n")) {
    const match = line.match(/^【([^】]+)】/);
    if (match) {
      if (current.text.length > 0) {
        segments.push({ speaker: current.speaker, text: current.text.join("\n") });
      }
      current = { speaker: match[1], text: [line.slice(match[0].length)] };
    } else {
      current.text.push(line);
    }
  }
  if (current.text.length > 0) {
    segments.push({ speaker: current.speaker, text: current.text.join("\n") });
  }
  return segments;
}
