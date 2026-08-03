import { useCallback, useEffect, useState } from "react";
import { listPersons } from "@/api/persons";
import {
  createPracticeSession,
  generateBackground,
  listTagLibrary,
  type TagLibrary,
} from "@/api/p2";
import type { Person } from "@/api/types";
import { Button } from "@/components/ui/button";
import { ErrorText, TextArea, TextInput } from "@/components/ui/field";
import { useRouter } from "@/lib/router";

const CHANNELS = [
  { value: "offline", label: "线下社交" },
  { value: "online", label: "线上（微信等）" },
] as const;

type Channel = (typeof CHANNELS)[number]["value"];

export function PracticePage() {
  const { navigate } = useRouter();
  const [persons, setPersons] = useState<Person[]>([]);
  const [tagLibrary, setTagLibrary] = useState<TagLibrary | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [channel, setChannel] = useState<Channel>("offline");
  const [mode, setMode] = useState<"tags" | "custom">("tags");
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [customTags, setCustomTags] = useState<string[]>([]);
  const [customTagInput, setCustomTagInput] = useState("");
  const [selectedPersons, setSelectedPersons] = useState<string[]>([]);
  const [customPrompt, setCustomPrompt] = useState("");
  const [background, setBackground] = useState("");
  const [generating, setGenerating] = useState(false);
  const [starting, setStarting] = useState(false);

  const invalidateBackground = () => setBackground("");

  const load = useCallback(async () => {
    try {
      const [p, tags] = await Promise.all([
        listPersons({ pageSize: 100 }),
        listTagLibrary(),
      ]);
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
    invalidateBackground();
    setSelectedTags((prev) =>
      prev.includes(tag) ? prev.filter((item) => item !== tag) : [...prev, tag],
    );
  };

  const addCustomTag = () => {
    const tag = customTagInput.trim();
    if (!tag) {
      return;
    }
    if (!customTags.includes(tag) && !selectedTags.includes(tag)) {
      setCustomTags((prev) => [...prev, tag]);
      invalidateBackground();
    }
    setCustomTagInput("");
  };

  const removeCustomTag = (tag: string) => {
    invalidateBackground();
    setCustomTags((prev) => prev.filter((item) => item !== tag));
  };

  const togglePerson = (personId: string) => {
    invalidateBackground();
    setSelectedPersons((prev) =>
      prev.includes(personId)
        ? prev.filter((item) => item !== personId)
        : [...prev, personId],
    );
  };

  const allTags = [...selectedTags, ...customTags];
  const canGenerate =
    mode === "custom"
      ? customPrompt.trim().length > 0 || selectedPersons.length > 0
      : allTags.length > 0 || selectedPersons.length > 0;

  const runGenerate = async () => {
    setGenerating(true);
    setError(null);
    try {
      const text = await generateBackground({
        channel,
        tags: mode === "tags" ? allTags : [],
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

  const startPractice = async () => {
    if (!background.trim()) {
      setError("请先生成社交背景");
      return;
    }
    setStarting(true);
    setError(null);
    try {
      const participants = persons
        .filter((person) => selectedPersons.includes(person.id))
        .map((person) => ({
          name: person.name,
          role: person.relationship_type ?? "在场者",
          person_id: person.id,
        }));
      const created = await createPracticeSession(null, {
        channel,
        tags: mode === "tags" ? allTags : [],
        custom_prompt: background,
        participants,
      });
      navigate(`/practice/session/${created.id}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "创建失败");
    } finally {
      setStarting(false);
    }
  };

  return (
    <main className="mx-auto w-full max-w-5xl space-y-6 px-6 py-10">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold tracking-tight">社交练习</h1>
        <Button variant="outline" size="sm" onClick={() => navigate("/practice/session")}>
          查看练习会话
        </Button>
      </div>
      <ErrorText message={error} />

      <section className="space-y-4 rounded-lg border bg-card p-4">
        <div>
          <h2 className="mb-2 text-sm font-medium text-muted-foreground">1. 选择交流渠道</h2>
          <div className="flex flex-wrap gap-2">
            {CHANNELS.map((item) => (
              <label
                key={item.value}
                className="flex cursor-pointer items-center gap-1.5 rounded border px-3 py-1.5 text-sm"
              >
                <input
                  type="radio"
                  name="channel"
                  checked={channel === item.value}
                  onChange={() => {
                    invalidateBackground();
                    setChannel(item.value);
                  }}
                />
                {item.label}
              </label>
            ))}
          </div>
        </div>

        <div>
          <h2 className="mb-2 text-sm font-medium text-muted-foreground">2. 定义场景</h2>
          <div className="mb-3 flex gap-2">
            <Button
              variant={mode === "tags" ? "default" : "outline"}
              size="sm"
              onClick={() => {
                invalidateBackground();
                setMode("tags");
              }}
            >
              用标签组合
            </Button>
            <Button
              variant={mode === "custom" ? "default" : "outline"}
              size="sm"
              onClick={() => {
                invalidateBackground();
                setMode("custom");
              }}
            >
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

              {customTags.length > 0 && (
                <div>
                  <p className="mb-1 text-sm text-muted-foreground">自定义标签</p>
                  <div className="flex flex-wrap gap-1.5">
                    {customTags.map((tag) => (
                      <span
                        key={tag}
                        className="inline-flex items-center gap-1 rounded-full border border-primary bg-secondary px-2.5 py-1 text-xs"
                      >
                        {tag}
                        <button
                          type="button"
                          onClick={() => removeCustomTag(tag)}
                          aria-label={`删除自定义标签 ${tag}`}
                          className="text-muted-foreground hover:text-foreground"
                        >
                          ×
                        </button>
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex gap-2">
                <TextInput
                  className="w-64"
                  placeholder="自定义标签（如：对方刚失恋、最近升职）"
                  value={customTagInput}
                  onChange={(e) => setCustomTagInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      e.preventDefault();
                      addCustomTag();
                    }
                  }}
                />
                <Button variant="outline" size="sm" onClick={addCustomTag}>
                  添加标签
                </Button>
              </div>
              <p className="text-xs text-muted-foreground">
                自定义标签与所选标签会一起交给 AI 用于扩写背景。
              </p>
            </div>
          ) : (
            <TextArea
              placeholder="用一两句话描述你的社交场景，例如：公司年会，我作为新人第一次参加，想认识市场部的小王……"
              value={customPrompt}
              onChange={(e) => {
                invalidateBackground();
                setCustomPrompt(e.target.value);
              }}
            />
          )}
        </div>

        <div>
          <h2 className="mb-2 text-sm font-medium text-muted-foreground">3. 选择在场对象（来自人物库，可多选）</h2>
          {persons.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              人物库为空，可以先在「人物」页面添加人物，或跳过此步。
            </p>
          ) : (
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
          )}
          {selectedPersons.length > 0 && (
            <p className="mt-1 text-xs text-muted-foreground">
              已选 {selectedPersons.length} 人：这些对象在人物库中的关系、熟悉度与已确认信息会提供给 AI。
            </p>
          )}
        </div>

        <div className="flex flex-wrap gap-2">
          <Button onClick={() => void runGenerate()} disabled={generating || !canGenerate}>
            {generating ? "生成中…" : "生成社交背景"}
          </Button>
          {background && (
            <Button variant="outline" onClick={() => void startPractice()} disabled={starting}>
              {starting ? "创建中…" : "基于此背景开始练习"}
            </Button>
          )}
        </div>

        {background && (
          <div className="space-y-1">
            <p className="text-sm font-medium text-muted-foreground">生成的场景背景</p>
            <p className="whitespace-pre-wrap rounded border bg-background p-3 text-sm">
              {background}
            </p>
          </div>
        )}
      </section>
    </main>
  );
}
