import { useCallback, useEffect, useState, type FormEvent } from "react";
import { listPersons } from "@/api/persons";
import {
  createPracticeSession,
  evaluateSession,
  generateBackground,
  listPracticeMessages,
  listPracticeSessions,
  listScenarios,
  listTagLibrary,
  practiceSendStream,
  type PracticeMessageItem,
  type PracticeSessionInfo,
  type Scenario,
  type TagLibrary,
} from "@/api/p2";
import type { Person } from "@/api/types";
import { Button } from "@/components/ui/button";
import { ErrorText, TextArea, TextInput } from "@/components/ui/field";
import { parseSse } from "@/utils/sse";

const CHANNELS = [
  { value: "offline", label: "线下社交" },
  { value: "online", label: "线上（微信等）" },
];

export function PracticePage() {
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [sessions, setSessions] = useState<PracticeSessionInfo[]>([]);
  const [persons, setPersons] = useState<Person[]>([]);
  const [tagLibrary, setTagLibrary] = useState<TagLibrary | null>(null);
  const [error, setError] = useState<string | null>(null);

  // 自定义向导
  const [channel, setChannel] = useState("offline");
  const [mode, setMode] = useState<"tags" | "custom">("tags");
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [customTag, setCustomTag] = useState("");
  const [selectedPersons, setSelectedPersons] = useState<string[]>([]);
  const [customPrompt, setCustomPrompt] = useState("");
  const [background, setBackground] = useState("");
  const [generating, setGenerating] = useState(false);

  // 会话
  const [sessionId, setSessionId] = useState("");
  const [sessionInfo, setSessionInfo] = useState<PracticeSessionInfo | null>(null);
  const [messages, setMessages] = useState<PracticeMessageItem[]>([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [evaluation, setEvaluation] = useState<{
    scores: Record<string, number>;
    summary: string;
  } | null>(null);

  const load = useCallback(async () => {
    try {
      const [s, sess, p, tags] = await Promise.all([
        listScenarios(),
        listPracticeSessions(),
        listPersons({ pageSize: 100 }),
        listTagLibrary(),
      ]);
      setScenarios(s);
      setSessions(sess);
      setPersons(p.items);
      setTagLibrary(tags);
    } catch (e) {
      setError(e instanceof Error ? e.message : "加载失败");
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const toggleTag = (tag: string) => {
    setSelectedTags((prev) =>
      prev.includes(tag) ? prev.filter((item) => item !== tag) : [...prev, tag],
    );
  };

  const addCustomTag = () => {
    const tag = customTag.trim();
    if (!tag) {
      return;
    }
    setSelectedTags((prev) => (prev.includes(tag) ? prev : [...prev, tag]));
    setCustomTag("");
  };

  const togglePerson = (personId: string) => {
    setSelectedPersons((prev) =>
      prev.includes(personId) ? prev.filter((item) => item !== personId) : [...prev, personId],
    );
  };

  const runGenerate = async () => {
    setGenerating(true);
    setError(null);
    try {
      const text = await generateBackground({
        channel,
        tags: mode === "tags" ? selectedTags : [],
        custom_prompt: mode === "custom" ? customPrompt : null,
        person_ids: selectedPersons,
      });
      setBackground(text);
    } catch (e) {
      setError(e instanceof Error ? e.message : "生成失败");
    } finally {
      setGenerating(false);
    }
  };

  const startCustom = async () => {
    if (!background.trim()) {
      setError("请先生成社交背景");
      return;
    }
    try {
      const participants = persons
        .filter((person) => selectedPersons.includes(person.id))
        .map((person) => ({ name: person.name, role: person.relationship_type ?? "在场者" }));
      const created = await createPracticeSession(scenarios[0]?.id ?? "", {
        channel,
        tags: selectedTags,
        custom_prompt: background,
        participants,
      });
      setSessionId(created.id);
      setSessionInfo({ ...created, status: "active", created_at: new Date().toISOString() });
      setMessages([]);
      setEvaluation(null);
      void load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "创建失败");
    }
  };

  const startPreset = async (scenario: Scenario) => {
    try {
      const created = await createPracticeSession(scenario.id);
      setSessionId(created.id);
      setSessionInfo({ ...created, status: "active", created_at: new Date().toISOString() });
      setMessages([]);
      setEvaluation(null);
      void load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "创建失败");
    }
  };

  const openSession = async (info: PracticeSessionInfo) => {
    setSessionId(info.id);
    setSessionInfo(info);
    setEvaluation(null);
    setMessages(await listPracticeMessages(info.id));
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

      <section className="space-y-3 rounded-lg border bg-card p-4">
        <h2 className="text-sm font-medium text-muted-foreground">自定义场景</h2>
        <div className="flex flex-wrap gap-2">
          {CHANNELS.map((item) => (
            <label key={item.value} className="flex cursor-pointer items-center gap-1.5 rounded border px-3 py-1.5 text-sm">
              <input
                type="radio"
                name="channel"
                checked={channel === item.value}
                onChange={() => setChannel(item.value)}
              />
              {item.label}
            </label>
          ))}
        </div>

        <div className="flex gap-2">
          <Button variant={mode === "tags" ? "default" : "outline"} size="sm" onClick={() => setMode("tags")}>
            用标签组合
          </Button>
          <Button variant={mode === "custom" ? "default" : "outline"} size="sm" onClick={() => setMode("custom")}>
            自定义提示词
          </Button>
        </div>

        {mode === "tags" ? (
          <div className="space-y-3">
            {tagLibrary &&
              Object.entries(tagLibrary).map(([group, tags]) => (
                <div key={group}>
                  <p className="mb-1 text-sm text-muted-foreground">{group}</p>
                  <div className="flex flex-wrap gap-1.5">
                    {tags.map((tag: string) => (
                      <button
                        key={tag}
                        type="button"
                        onClick={() => toggleTag(tag)}
                        className={`rounded-full border px-2.5 py-1 text-xs ${
                          selectedTags.includes(tag)
                            ? "border-primary bg-primary text-primary-foreground"
                            : "hover:bg-accent"
                        }`}
                      >
                        {tag}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            <div className="flex gap-2">
              <TextInput
                className="w-56"
                placeholder="自定义标签（如：对方刚失恋）"
                value={customTag}
                onChange={(e) => setCustomTag(e.target.value)}
              />
              <Button variant="outline" size="sm" onClick={addCustomTag}>
                添加标签
              </Button>
            </div>
          </div>
        ) : (
          <TextArea
            placeholder="用一两句话描述你的社交场景，例如：公司年会，我作为新人第一次参加，想认识市场部的小王……"
            value={customPrompt}
            onChange={(e) => setCustomPrompt(e.target.value)}
          />
        )}

        <div>
          <p className="mb-1 text-sm text-muted-foreground">选择在场对象（来自人物库，可多选）</p>
          <div className="flex flex-wrap gap-1.5">
            {persons.map((person) => (
              <button
                key={person.id}
                type="button"
                onClick={() => togglePerson(person.id)}
                className={`rounded-full border px-2.5 py-1 text-xs ${
                  selectedPersons.includes(person.id)
                    ? "border-primary bg-primary text-primary-foreground"
                    : "hover:bg-accent"
                }`}
              >
                {person.name}
              </button>
            ))}
          </div>
        </div>

        <div className="flex gap-2">
          <Button onClick={() => void runGenerate()} disabled={generating}>
            {generating ? "生成中…" : "生成社交背景"}
          </Button>
          {background && (
            <Button variant="outline" onClick={() => void startCustom()}>
              基于此背景开始练习
            </Button>
          )}
        </div>
        {background && (
          <p className="whitespace-pre-wrap rounded border bg-background p-3 text-sm text-muted-foreground">
            {background}
          </p>
        )}
      </section>

      <section className="space-y-2">
        <h2 className="text-sm font-medium text-muted-foreground">或使用预设场景</h2>
        <div className="flex flex-wrap gap-2">
          {scenarios.map((scenario) => (
            <Button key={scenario.id} variant="outline" size="sm" onClick={() => void startPreset(scenario)}>
              {scenario.title}
            </Button>
          ))}
        </div>
      </section>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-[220px_1fr]">
        <aside className="space-y-1">
          <h2 className="text-sm font-medium text-muted-foreground">练习会话</h2>
          {sessions.map((session) => (
            <button
              key={session.id}
              type="button"
              onClick={() => void openSession(session)}
              className={`block w-full truncate rounded px-2 py-1.5 text-left text-sm ${
                sessionId === session.id ? "bg-secondary font-medium" : "hover:bg-accent"
              }`}
            >
              {session.title} {session.status === "completed" ? "（已完成）" : ""}
            </button>
          ))}
        </aside>

        <section className="space-y-3">
          {sessionInfo && sessionInfo.participants.length > 0 && (
            <div className="rounded-lg border bg-card p-2 text-sm text-muted-foreground">
              在场角色：{sessionInfo.participants.map((p) => p.name).join("、")}
            </div>
          )}
          <div className="space-y-3 rounded-lg border bg-card p-4">
            {messages.length === 0 && (
              <p className="text-center text-sm text-muted-foreground">开始练习后与 AI 角色对话</p>
            )}
            {messages.flatMap((message) => renderBubbles(message))}
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
              {evaluation.summary && (
                <p className="text-sm text-muted-foreground">{evaluation.summary}</p>
              )}
            </div>
          )}
        </section>
      </div>
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
  return segments.map((segment, index) => {
    return (
      <div key={`${message.id}-${index}`} className="flex justify-start">
        <div className="max-w-[80%] whitespace-pre-wrap rounded-lg border bg-background px-3 py-2 text-sm">
          {segment.speaker && (
            <span className="mr-1 text-xs font-medium text-primary">{segment.speaker}</span>
          )}
          {segment.text}
        </div>
      </div>
    );
  });
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
