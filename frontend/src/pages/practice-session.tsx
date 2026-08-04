import { useEffect, useMemo, useState, type FormEvent } from "react";
import {
  deletePracticeSession,
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
import { extractRoleNames, type DetectedRole } from "@/lib/practice-roles";
import { parseSse } from "@/utils/sse";

const CHANNEL_LABELS: Record<string, string> = {
  online: "线上（微信等）",
  offline: "线下社交",
};

const SPEAKER_STYLES = [
  {
    avatar: "bg-sky-500",
    name: "text-sky-600 dark:text-sky-400",
    bubble: "border-sky-200 bg-sky-50 dark:border-sky-800 dark:bg-sky-950/40",
  },
  {
    avatar: "bg-emerald-500",
    name: "text-emerald-600 dark:text-emerald-400",
    bubble: "border-emerald-200 bg-emerald-50 dark:border-emerald-800 dark:bg-emerald-950/40",
  },
  {
    avatar: "bg-amber-500",
    name: "text-amber-600 dark:text-amber-400",
    bubble: "border-amber-200 bg-amber-50 dark:border-amber-800 dark:bg-amber-950/40",
  },
  {
    avatar: "bg-violet-500",
    name: "text-violet-600 dark:text-violet-400",
    bubble: "border-violet-200 bg-violet-50 dark:border-violet-800 dark:bg-violet-950/40",
  },
  {
    avatar: "bg-rose-500",
    name: "text-rose-600 dark:text-rose-400",
    bubble: "border-rose-200 bg-rose-50 dark:border-rose-800 dark:bg-rose-950/40",
  },
  {
    avatar: "bg-teal-500",
    name: "text-teal-600 dark:text-teal-400",
    bubble: "border-teal-200 bg-teal-50 dark:border-teal-800 dark:bg-teal-950/40",
  },
] as const;

type SpeakerStyle = (typeof SPEAKER_STYLES)[number];

function speakerStyle(name: string): SpeakerStyle {
  let hash = 0;
  for (const ch of name) {
    hash = (hash * 31 + (ch.codePointAt(0) ?? 0)) >>> 0;
  }
  return SPEAKER_STYLES[hash % SPEAKER_STYLES.length] ?? SPEAKER_STYLES[0];
}

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
  const isMulti = (sessionInfo?.participants.length ?? 0) > 1;
  const roleNames = useMemo(() => {
    const background = sessionInfo?.custom_prompt ?? "";
    const conversation = messages.map((m) => m.content).join("\n");
    return extractRoleNames(`${background}\n${conversation}`);
  }, [sessionInfo?.custom_prompt, messages]);
  const displayRoles =
    roleNames.length > 0
      ? roleNames
      : (sessionInfo?.participants ?? []).map((p) => ({
          name: p.name,
          role: p.role,
        }));

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

  const handleDelete = async (id: string) => {
    const target = sessions.find((item) => item.id === id);
    if (
      !window.confirm(`确认删除会话「${target?.title ?? "该会话"}」？删除后不可恢复。`)
    ) {
      return;
    }
    try {
      await deletePracticeSession(id);
      const remaining = sessions.filter((item) => item.id !== id);
      setSessions(remaining);
      if (currentId === id) {
        const next = remaining[0] ?? null;
        setCurrentId(next ? next.id : null);
        setSessionInfo(next ?? null);
        setEvaluation(null);
        setMessages(next ? await listPracticeMessages(next.id) : []);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "删除失败");
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
              <div key={session.id} className="group flex items-center gap-0.5">
                <button
                  type="button"
                  onClick={() => void openSession(session.id)}
                  className={`block min-w-0 flex-1 truncate rounded px-2 py-1.5 text-left text-sm ${
                    currentId === session.id
                      ? "bg-secondary font-medium"
                      : "hover:bg-accent"
                  }`}
                >
                  {session.title}
                  {session.status === "completed" ? "（已完成）" : ""}
                </button>
                <button
                  type="button"
                  onClick={() => void handleDelete(session.id)}
                  aria-label={`删除会话 ${session.title}`}
                  title="删除会话"
                  className="rounded px-1 text-muted-foreground opacity-0 transition-opacity hover:text-destructive focus:opacity-100 group-hover:opacity-100"
                >
                  ×
                </button>
              </div>
            ))}
          </aside>

          <section className="space-y-3">
            {sessionInfo && (
              <div className="space-y-1 rounded-lg border bg-card p-3 text-sm text-muted-foreground">
                <p>
                  渠道：{CHANNEL_LABELS[sessionInfo.channel] ?? sessionInfo.channel}
                  {sessionInfo.tags.length > 0 && <> · 标签：{sessionInfo.tags.join("、")}</>}
                </p>
                {displayRoles.length > 0 ? (
                  <p>
                    场景角色：
                    {displayRoles
                      .map((r) => (r.role ? `${r.name}（${r.role}）` : r.name))
                      .join("、")}
                  </p>
                ) : (
                  <p>场景角色：对方（未在场景中识别到明确角色名）</p>
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
                  {isMulti
                    ? "开始练习后与 AI 角色对话，角色之间也会互相交流"
                    : "开始练习后与对方一对一对话"}
                </p>
              )}
              {messages.flatMap((message) => renderBubbles(message, displayRoles))}
            </div>

            <form onSubmit={(e) => void send(e)} className="flex gap-2">
              <TextArea
                className="min-h-16"
                placeholder={
                  isMulti ? "输入你的回应，也可以暂时旁观角色们聊天…" : "输入你的回应…"
                }
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

function renderBubbles(
  message: PracticeMessageItem,
  roles: DetectedRole[],
): React.ReactNode[] {
  if (message.role === "user") {
    return [
      <div key={message.id} className="flex items-start justify-end gap-2">
        <div className="max-w-[75%] whitespace-pre-wrap rounded-lg border bg-primary px-3 py-2 text-sm text-primary-foreground">
          {message.content}
        </div>
        <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-primary text-xs font-semibold text-primary-foreground">
          我
        </div>
      </div>,
    ];
  }
  const segments = splitBySpeaker(message.content);
  return segments.map((segment, index) => {
    const speaker = resolveSpeaker(segment.speaker, roles);
    const style = speakerStyle(speaker.name);
    const label = speaker.role ? `${speaker.name}（${speaker.role}）` : speaker.name;
    return (
      <div key={`${message.id}-${index}`} className="flex items-start gap-2">
        <div
          className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs font-semibold text-white ${style.avatar}`}
        >
          {speaker.name.slice(0, 1)}
        </div>
        <div className={`max-w-[75%] rounded-lg border px-3 py-2 text-sm ${style.bubble}`}>
          <p className={`mb-0.5 text-xs font-semibold ${style.name}`}>{label}</p>
          <p className="whitespace-pre-wrap">{segment.text}</p>
        </div>
      </div>
    );
  });
}

function resolveSpeaker(raw: string | undefined, roles: DetectedRole[]): DetectedRole {
  if (raw) {
    const match = roles.find(
      (role) => raw.includes(role.name) || role.name.includes(raw),
    );
    if (match) {
      return match;
    }
    return { name: raw };
  }
  return roles[0] ?? { name: "对方" };
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
