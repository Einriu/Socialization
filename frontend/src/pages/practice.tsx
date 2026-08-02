import { useCallback, useEffect, useState, type FormEvent } from "react";
import {
  createPracticeSession,
  evaluateSession,
  listPracticeMessages,
  listPracticeSessions,
  listScenarios,
  practiceSendStream,
  type PracticeMessageItem,
  type PracticeSessionInfo,
  type Scenario,
} from "@/api/p2";
import { Button } from "@/components/ui/button";
import { ErrorText, Select, TextArea } from "@/components/ui/field";
import { parseSse } from "@/utils/sse";

export function PracticePage() {
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [sessions, setSessions] = useState<PracticeSessionInfo[]>([]);
  const [scenarioId, setScenarioId] = useState("");
  const [sessionId, setSessionId] = useState("");
  const [messages, setMessages] = useState<PracticeMessageItem[]>([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [evaluation, setEvaluation] = useState<{ scores: Record<string, number>; summary: string } | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const [s, sess] = await Promise.all([listScenarios(), listPracticeSessions()]);
      setScenarios(s);
      setSessions(sess);
    } catch (e) {
      setError(e instanceof Error ? e.message : "加载失败");
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const startSession = async () => {
    if (!scenarioId) {
      return;
    }
    try {
      const created = await createPracticeSession(scenarioId);
      setSessionId(created.id);
      setMessages([]);
      setEvaluation(null);
      void load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "创建失败");
    }
  };

  const openSession = async (id: string) => {
    setSessionId(id);
    setEvaluation(null);
    setMessages(await listPracticeMessages(id));
  };

  const send = async (e: FormEvent) => {
    e.preventDefault();
    if (!sessionId || !input.trim() || streaming) {
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
      const response = await practiceSendStream(sessionId, userMessage.content);
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
    } catch (e) {
      setError(e instanceof Error ? e.message : "发送失败");
    } finally {
      setStreaming(false);
    }
  };

  const evaluate = async () => {
    if (!sessionId) {
      return;
    }
    try {
      setEvaluation(await evaluateSession(sessionId));
      void load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "评分失败");
    }
  };

  return (
    <main className="mx-auto w-full max-w-5xl space-y-6 px-6 py-10">
      <h1 className="text-2xl font-semibold tracking-tight">社交练习</h1>
      <ErrorText message={error} />

      <div className="flex flex-wrap items-end gap-3 rounded-lg border bg-card p-4">
        <Select className="w-64" value={scenarioId} onChange={(e) => setScenarioId(e.target.value)}>
          <option value="">选择练习场景</option>
          {scenarios.map((scenario) => (
            <option key={scenario.id} value={scenario.id}>
              {scenario.title}
            </option>
          ))}
        </Select>
        <Button onClick={() => void startSession()}>开始练习</Button>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-[220px_1fr]">
        <aside className="space-y-1">
          <h2 className="text-sm font-medium text-muted-foreground">练习会话</h2>
          {sessions.map((session) => (
            <button
              key={session.id}
              type="button"
              onClick={() => void openSession(session.id)}
              className={`block w-full truncate rounded px-2 py-1.5 text-left text-sm ${
                sessionId === session.id ? "bg-secondary font-medium" : "hover:bg-accent"
              }`}
            >
              {session.title} {session.status === "completed" ? "（已完成）" : ""}
            </button>
          ))}
        </aside>

        <section className="space-y-3">
          <div className="space-y-3 rounded-lg border bg-card p-4">
            {messages.length === 0 && (
              <p className="text-center text-sm text-muted-foreground">开始练习后与 AI 对话</p>
            )}
            {messages.map((message) => (
              <div key={message.id} className={message.role === "user" ? "flex justify-end" : "flex justify-start"}>
                <div
                  className={`max-w-[80%] whitespace-pre-wrap rounded-lg border px-3 py-2 text-sm ${
                    message.role === "user" ? "bg-primary text-primary-foreground" : "bg-background"
                  }`}
                >
                  {message.content || "…"}
                </div>
              </div>
            ))}
          </div>
          <form onSubmit={(e) => void send(e)} className="flex gap-2">
            <TextArea
              className="min-h-16"
              placeholder="输入你的回应…"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={streaming || !sessionId}
            />
            <Button type="submit" disabled={streaming || !input.trim()}>
              {streaming ? "对话中…" : "发送"}
            </Button>
          </form>
          {sessionId && !streaming && (
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
              {evaluation.summary && <p className="text-sm text-muted-foreground">{evaluation.summary}</p>}
            </div>
          )}
        </section>
      </div>
    </main>
  );
}
