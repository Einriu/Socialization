import { useCallback, useEffect, useRef, useState, type FormEvent } from "react";
import {
  cancelGeneration,
  createConversation,
  deleteConversation,
  getMessages,
  listConversations,
  regenerateStream,
  sendMessageStream,
  setLinks,
  updateConversation,
} from "@/api/conversations";
import { listPersons } from "@/api/persons";
import { listModels, listProviders } from "@/api/providers";
import { listTopics } from "@/api/topics";
import { listDocuments } from "@/api/documents";
import type {
  AIModel,
  Citation,
  Conversation,
  DocumentRecord,
  Person,
  Provider,
  Topic,
} from "@/api/types";
import { Button } from "@/components/ui/button";
import { ErrorText, Select, TextArea } from "@/components/ui/field";
import { parseSse } from "@/utils/sse";

interface LocalMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  status: string;
  generated_by_ai: boolean;
  metadata: { citations?: Citation[] } | null;
}

export function AssistantPage() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentId, setCurrentId] = useState("");
  const [messages, setMessages] = useState<LocalMessage[]>([]);
  const [providers, setProviders] = useState<Provider[]>([]);
  const [models, setModels] = useState<AIModel[]>([]);
  const [persons, setPersons] = useState<Person[]>([]);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [providerId, setProviderId] = useState("");
  const [modelId, setModelId] = useState("");
  const [linkPersonId, setLinkPersonId] = useState("");
  const [linkTopicId, setLinkTopicId] = useState("");
  const [linkDocumentId, setLinkDocumentId] = useState("");
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const loadConversations = useCallback(async () => {
    try {
      const data = await listConversations();
      setConversations(data.items);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "加载会话失败");
    }
  }, []);

  const loadOptions = useCallback(async () => {
    try {
      const [p, t, personsData, docs] = await Promise.all([
        listProviders(),
        listTopics({ pageSize: 100 }),
        listPersons({ pageSize: 100 }),
        listDocuments({ pageSize: 100 }),
      ]);
      setProviders(p.items);
      setTopics(t.items);
      setPersons(personsData.items);
      setDocuments(docs.items);
    } catch (e) {
      setError(e instanceof Error ? e.message : "加载选项失败");
    }
  }, []);

  useEffect(() => {
    void loadConversations();
    void loadOptions();
  }, [loadConversations, loadOptions]);

  useEffect(() => {
    if (!providerId) {
      setModels([]);
      return;
    }
    void listModels(providerId)
      .then(setModels)
      .catch(() => setModels([]));
  }, [providerId]);

  const openConversation = useCallback(
    async (conversation: Conversation) => {
      setCurrentId(conversation.id);
      setProviderId(conversation.provider_id ?? "");
      setModelId(conversation.model_id ?? "");
      const personLink = conversation.links.find((link) => link.person_id);
      const topicLink = conversation.links.find((link) => link.topic_id);
      setLinkPersonId(personLink?.person_id ?? "");
      setLinkTopicId(topicLink?.topic_id ?? "");
      try {
        const data = await getMessages(conversation.id);
        setMessages(
          data.items.map((item) => ({
            id: item.id,
            role: item.role as "user" | "assistant",
            content: item.content ?? "",
            status: item.status,
            generated_by_ai: item.generated_by_ai,
            metadata: item.metadata ?? null,
          })),
        );
      } catch (e) {
        setError(e instanceof Error ? e.message : "加载消息失败");
      }
    },
    [],
  );

  const newConversation = async () => {
    try {
      const created = await createConversation({});
      setConversations((prev) => [created, ...prev]);
      await openConversation(created);
    } catch (e) {
      setError(e instanceof Error ? e.message : "创建会话失败");
    }
  };

  const handleRemove = async (conversation: Conversation) => {
    if (!window.confirm(`确认删除会话「${conversation.title}」？`)) {
      return;
    }
    await deleteConversation(conversation.id);
    if (currentId === conversation.id) {
      setCurrentId("");
      setMessages([]);
    }
    void loadConversations();
  };

  const saveSettings = async () => {
    if (!currentId) {
      return;
    }
    await updateConversation(currentId, {
      provider_id: providerId || null,
      model_id: modelId || null,
    });
    await setLinks(currentId, {
      person_id: linkPersonId || null,
      topic_id: linkTopicId || null,
      document_id: linkDocumentId || null,
    });
    void loadConversations();
  };

  const send = async (content: string) => {
    if (!currentId || !content.trim() || streaming) {
      return;
    }
    const userMessage: LocalMessage = {
      id: `local-user-${Date.now()}`,
      role: "user",
      content: content.trim(),
      status: "completed",
      generated_by_ai: false,
      metadata: null,
    };
    const assistantMessage: LocalMessage = {
      id: `local-ai-${Date.now()}`,
      role: "assistant",
      content: "",
      status: "generating",
      generated_by_ai: true,
      metadata: null,
    };
    setMessages((prev) => [...prev, userMessage, assistantMessage]);
    setInput("");
    setStreaming(true);
    setError(null);
    const controller = new AbortController();
    abortRef.current = controller;
    try {
      const response = await sendMessageStream(currentId, content, modelId || null, controller.signal);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      for await (const event of parseSse(response)) {
        if (event.type === "delta") {
          setMessages((prev) =>
            prev.map((item) =>
              item.id === assistantMessage.id
                ? { ...item, content: item.content + String(event.content ?? "") }
                : item,
            ),
          );
        } else if (event.type === "done") {
          setMessages((prev) =>
            prev.map((item) =>
              item.id === assistantMessage.id
                ? {
                    ...item,
                    status: String(event.status ?? "completed"),
                    metadata: {
                      citations: (event.citations as Citation[] | undefined) ?? [],
                    },
                  }
                : item,
            ),
          );
        } else if (event.type === "error") {
          setError(String(event.message ?? "生成失败"));
          setMessages((prev) =>
            prev.map((item) =>
              item.id === assistantMessage.id ? { ...item, status: "failed" } : item,
            ),
          );
        }
      }
    } catch (e) {
      setError(e instanceof Error && e.name !== "AbortError" ? e.message : "已停止生成");
      setMessages((prev) =>
        prev.map((item) =>
          item.id === assistantMessage.id ? { ...item, status: "stopped" } : item,
        ),
      );
    } finally {
      setStreaming(false);
      abortRef.current = null;
    }
  };

  const stop = async () => {
    abortRef.current?.abort();
    if (currentId) {
      await cancelGeneration(currentId).catch(() => undefined);
    }
  };

  const regenerate = async (messageId: string) => {
    if (!currentId || streaming) {
      return;
    }
    setStreaming(true);
    setMessages((prev) =>
      prev.map((item) =>
        item.id === messageId ? { ...item, content: "", status: "generating" } : item,
      ),
    );
    const controller = new AbortController();
    abortRef.current = controller;
    try {
      const response = await regenerateStream(currentId, messageId, controller.signal);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      for await (const event of parseSse(response)) {
        if (event.type === "delta") {
          setMessages((prev) =>
            prev.map((item) =>
              item.id === messageId
                ? { ...item, content: item.content + String(event.content ?? "") }
                : item,
            ),
          );
        }
        if (event.type === "done") {
          setMessages((prev) =>
            prev.map((item) =>
              item.id === messageId ? { ...item, status: "completed" } : item,
            ),
          );
        }
      }
    } catch (e) {
      setError(e instanceof Error && e.name !== "AbortError" ? e.message : "已停止生成");
    } finally {
      setStreaming(false);
      abortRef.current = null;
    }
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    void send(input);
  };

  return (
    <main className="mx-auto w-full max-w-5xl space-y-4 px-6 py-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold tracking-tight">AI 助手</h1>
        <Button onClick={() => void newConversation()}>新建对话</Button>
      </div>
      <ErrorText message={error} />

      <div className="grid grid-cols-1 gap-4 md:grid-cols-[240px_1fr]">
        <aside className="space-y-2">
          <h2 className="text-sm font-medium text-muted-foreground">对话列表</h2>
          <ul className="space-y-1">
            {conversations.map((conversation) => (
              <li key={conversation.id}>
                <div className="flex items-center gap-1">
                  <button
                    type="button"
                    onClick={() => void openConversation(conversation)}
                    className={`flex-1 truncate rounded px-2 py-1.5 text-left text-sm ${
                      currentId === conversation.id ? "bg-secondary font-medium" : "hover:bg-accent"
                    }`}
                  >
                    {conversation.title}
                  </button>
                  <Button variant="ghost" size="sm" onClick={() => void handleRemove(conversation)}>
                    删
                  </Button>
                </div>
              </li>
            ))}
            {conversations.length === 0 && (
              <li className="text-sm text-muted-foreground">暂无对话</li>
            )}
          </ul>
        </aside>

        <section className="space-y-3">
          {!currentId ? (
            <div className="rounded-lg border bg-card p-10 text-center text-muted-foreground">
              选择或新建一个对话开始
            </div>
          ) : (
            <>
              <div className="flex flex-wrap items-end gap-3 rounded-lg border bg-card p-3">
                <Select className="w-48" value={providerId} onChange={(e) => setProviderId(e.target.value)} aria-label="提供商">
                  <option value="">未选择提供商</option>
                  {providers.filter((p) => p.enabled).map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name}
                    </option>
                  ))}
                </Select>
                <Select className="w-48" value={modelId} onChange={(e) => setModelId(e.target.value)} aria-label="模型">
                  <option value="">未选择模型</option>
                  {models.filter((m) => m.enabled).map((m) => (
                    <option key={m.id} value={m.id}>
                      {m.model_id}
                    </option>
                  ))}
                </Select>
                <Select className="w-44" value={linkPersonId} onChange={(e) => setLinkPersonId(e.target.value)} aria-label="关联人物">
                  <option value="">不关联人物</option>
                  {persons.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name}
                    </option>
                  ))}
                </Select>
                <Select className="w-44" value={linkTopicId} onChange={(e) => setLinkTopicId(e.target.value)} aria-label="关联话题">
                  <option value="">不关联话题</option>
                  {topics.map((t) => (
                    <option key={t.id} value={t.id}>
                      {t.name}
                    </option>
                  ))}
                </Select>
                <Select
                  className="w-44"
                  value={linkDocumentId}
                  onChange={(e) => setLinkDocumentId(e.target.value)}
                  aria-label="关联文件"
                >
                  <option value="">不关联文件</option>
                  {documents
                    .filter((d) => d.status === "completed")
                    .map((d) => (
                      <option key={d.id} value={d.id}>
                        {d.filename}
                      </option>
                    ))}
                </Select>
                <Button variant="outline" size="sm" onClick={() => void saveSettings()}>
                  应用设置
                </Button>
              </div>

              <div className="space-y-3 rounded-lg border bg-card p-4">
                {messages.length === 0 && (
                  <p className="text-center text-sm text-muted-foreground">发送第一条消息开始对话</p>
                )}
                {messages.map((message) => (
                  <div key={message.id} className={message.role === "user" ? "flex justify-end" : "flex justify-start"}>
                    <div
                      className={`max-w-[80%] rounded-lg border px-3 py-2 text-sm ${
                        message.role === "user" ? "bg-primary text-primary-foreground" : "bg-background"
                      }`}
                    >
                      <div className="whitespace-pre-wrap">{message.content || "…"}</div>
                      {message.generated_by_ai && (
                        <div className="mt-1 flex items-center gap-2 text-xs text-muted-foreground">
                          <span>AI 生成</span>
                          {message.status !== "completed" && <span>（{message.status}）</span>}
                          {!streaming && message.status === "completed" && (
                            <>
                              <button
                                type="button"
                                className="underline"
                                onClick={() => void regenerate(message.id)}
                              >
                                重新生成
                              </button>
                              <button
                                type="button"
                                className="underline"
                                onClick={() => void navigator.clipboard.writeText(message.content)}
                              >
                                复制
                              </button>
                            </>
                          )}
                          {message.metadata?.citations && message.metadata.citations.length > 0 && (
                            <span>
                              引用：
                              {message.metadata.citations
                                .map((citation) => citation.document_name)
                                .join("、")}
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>

              <form onSubmit={handleSubmit} className="space-y-2">
                <TextArea
                  placeholder="输入消息，Enter 发送（Shift+Enter 换行）"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      void send(input);
                    }
                  }}
                  disabled={streaming}
                />
                <div className="flex justify-end gap-2">
                  {streaming ? (
                    <Button variant="destructive" onClick={() => void stop()}>
                      停止生成
                    </Button>
                  ) : (
                    <Button type="submit" disabled={!input.trim()}>
                      发送
                    </Button>
                  )}
                </div>
              </form>
            </>
          )}
        </section>
      </div>
    </main>
  );
}
