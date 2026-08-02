import { useCallback, useEffect, useState, type FormEvent } from "react";
import {
  createDate,
  createFact,
  createFollowUp,
  deleteDate,
  deleteFact,
  deleteFollowUp,
  getPerson,
  getTimeline,
  listDates,
  listFacts,
  listFollowUps,
  setPersonTags,
  updateFollowUp,
} from "@/api/persons";
import { listTags } from "@/api/tags";
import {
  getCustomValues,
  listCustomFields,
  setCustomValues,
} from "@/api/custom-fields";
import { generateBriefing } from "@/api/p2";
import type {
  FollowUpTask,
  ImportantDate,
  Person,
  PersonFact,
  Tag,
  TimelineItem,
  CustomField,
} from "@/api/types";
import { Button } from "@/components/ui/button";
import { ErrorText, Field, Select, TextInput } from "@/components/ui/field";
import { formatDateTime } from "@/lib/datetime";
import { matchRoute, useRouter } from "@/lib/router";

const FACT_TYPES = ["喜好", "兴趣", "厌恶", "禁忌", "性格印象", "沟通风格", "近期目标", "正在处理的问题", "其他"];

function ConfidenceBadge({ confidence }: { confidence: string }) {
  const unconfirmed = confidence === "ai_inference" || confidence === "unconfirmed";
  return (
    <span
      className={`rounded px-1.5 py-0.5 text-xs ${
        unconfirmed ? "bg-amber-100 text-amber-700 dark:bg-amber-900 dark:text-amber-200" : "bg-secondary text-secondary-foreground"
      }`}
    >
      {unconfirmed ? "未确认" : "已确认"}
    </span>
  );
}

export function PersonDetailPage() {
  const { path, navigate } = useRouter();
  const personId = matchRoute(path, "/persons/:id")?.params.id ?? "";

  const [person, setPerson] = useState<Person | null>(null);
  const [allTags, setAllTags] = useState<Tag[]>([]);
  const [facts, setFacts] = useState<PersonFact[]>([]);
  const [dates, setDates] = useState<ImportantDate[]>([]);
  const [followUps, setFollowUps] = useState<FollowUpTask[]>([]);
  const [timeline, setTimeline] = useState<TimelineItem[]>([]);
  const [customFields, setCustomFields] = useState<CustomField[]>([]);
  const [customValues, setCustomValuesState] = useState<Record<string, unknown>>({});
  const [briefing, setBriefing] = useState("");
  const [error, setError] = useState<string | null>(null);

  // 事实表单
  const [factType, setFactType] = useState(FACT_TYPES[0] ?? "其他");
  const [factContent, setFactContent] = useState("");
  const [factSource, setFactSource] = useState("user");
  const [factSensitive, setFactSensitive] = useState(false);
  // 日期表单
  const [dateTitle, setDateTitle] = useState("");
  const [dateKind, setDateKind] = useState("birthday");
  const [dateValue, setDateValue] = useState("");
  // 跟进表单
  const [followUpTitle, setFollowUpTitle] = useState("");

  const load = useCallback(async () => {
    try {
      const [p, f, d, fu, t, tags, fields, values] = await Promise.all([
        getPerson(personId),
        listFacts(personId),
        listDates(personId),
        listFollowUps(personId),
        getTimeline(personId),
        listTags(),
        listCustomFields(),
        getCustomValues(personId),
      ]);
      setPerson(p);
      setFacts(f.items);
      setDates(d.items);
      setFollowUps(fu.items);
      setTimeline(t.items);
      setAllTags(tags.items);
      setCustomFields(fields);
      setCustomValuesState(values);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "加载失败");
    }
  }, [personId]);

  useEffect(() => {
    void load();
  }, [load]);

  if (!person) {
    return (
      <main className="mx-auto w-full max-w-4xl px-6 py-10">
        <ErrorText message={error} />
        {!error && <p className="text-muted-foreground">加载中…</p>}
      </main>
    );
  }

  const toggleTag = async (tagId: string, checked: boolean) => {
    const current = new Set(person.tags.map((t) => t.id));
    if (checked) {
      current.add(tagId);
    } else {
      current.delete(tagId);
    }
    try {
      await setPersonTags(personId, [...current]);
      void load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "更新标签失败");
    }
  };

  const addFact = async (e: FormEvent) => {
    e.preventDefault();
    if (!factContent.trim()) {
      return;
    }
    try {
      await createFact(personId, {
        fact_type: factType,
        content: factContent.trim(),
        source_type: factSource,
        confidence: factSource === "ai_inference" ? "ai_inference" : "confirmed",
        is_sensitive: factSensitive,
      });
      setFactContent("");
      void load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "添加事实失败");
    }
  };

  const addDate = async (e: FormEvent) => {
    e.preventDefault();
    if (!dateTitle.trim() || !dateValue) {
      return;
    }
    try {
      await createDate(personId, {
        title: dateTitle.trim(),
        kind: dateKind,
        date_value: dateValue,
      });
      setDateTitle("");
      setDateValue("");
      void load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "添加日期失败");
    }
  };

  const addFollowUp = async (e: FormEvent) => {
    e.preventDefault();
    if (!followUpTitle.trim()) {
      return;
    }
    try {
      await createFollowUp(personId, { title: followUpTitle.trim() });
      setFollowUpTitle("");
      void load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "添加跟进失败");
    }
  };

  const toggleFollowUp = async (task: FollowUpTask) => {
    try {
      await updateFollowUp(task.id, { completed: !task.completed });
      void load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "更新跟进失败");
    }
  };

  const saveCustomValue = async (fieldId: string, value: unknown) => {
    try {
      const values = await setCustomValues(personId, {
        ...customValues,
        [fieldId]: value,
      });
      setCustomValuesState(values);
    } catch (e) {
      setError(e instanceof Error ? e.message : "保存自定义字段失败");
    }
  };

  const loadBriefing = async () => {
    setBriefing("生成中…");
    try {
      setBriefing(await generateBriefing(personId));
    } catch (e) {
      setBriefing(e instanceof Error ? e.message : "生成失败");
    }
  };

  return (
    <main className="mx-auto w-full max-w-4xl space-y-8 px-6 py-10">
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <h1 className="text-2xl font-semibold tracking-tight">{person.name}</h1>
          <p className="text-muted-foreground">
            {[person.relationship_type, person.organization, person.occupation, person.location]
              .filter(Boolean)
              .join(" · ") || "暂无身份信息"}
            {" · "}熟悉程度 {person.familiarity_level}/6
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => void loadBriefing()}>
            聊天简报
          </Button>
          <Button variant="outline" onClick={() => navigate(`/persons/${person.id}/edit`)}>
            编辑
          </Button>
          <Button variant="ghost" onClick={() => navigate("/persons")}>
            返回
          </Button>
        </div>
      </div>

      <ErrorText message={error} />

      {person.summary && <p className="rounded-lg border bg-card p-4 text-sm">{person.summary}</p>}
      {briefing && (
        <section className="whitespace-pre-wrap rounded-lg border bg-card p-4 text-sm">{briefing}</section>
      )}

      <section className="space-y-3">
        <h2 className="text-lg font-medium">标签</h2>
        <div className="flex flex-wrap gap-2">
          {allTags.map((tag) => {
            const checked = person.tags.some((t) => t.id === tag.id);
            return (
              <label
                key={tag.id}
                className="flex cursor-pointer items-center gap-1.5 rounded border px-2.5 py-1 text-sm"
                style={checked && tag.color ? { borderColor: tag.color } : undefined}
              >
                <input
                  type="checkbox"
                  checked={checked}
                  onChange={(e) => void toggleTag(tag.id, e.target.checked)}
                />
                {tag.name}
              </label>
            );
          })}
        </div>
      </section>

      <section className="space-y-3">
        <h2 className="text-lg font-medium">人物事实</h2>
        <form onSubmit={(e) => void addFact(e)} className="grid grid-cols-1 gap-3 rounded-lg border bg-card p-4 md:grid-cols-4">
          <Select value={factType} onChange={(e) => setFactType(e.target.value)}>
            {FACT_TYPES.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </Select>
          <div className="md:col-span-3">
            <TextInput
              placeholder="内容，如：喜欢喝美式咖啡"
              value={factContent}
              onChange={(e) => setFactContent(e.target.value)}
            />
          </div>
          <Select value={factSource} onChange={(e) => setFactSource(e.target.value)}>
            <option value="user">用户记录</option>
            <option value="person">对方亲口表达</option>
            <option value="ai_inference">AI 推测（未确认）</option>
          </Select>
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" checked={factSensitive} onChange={(e) => setFactSensitive(e.target.checked)} />
            敏感信息
          </label>
          <Button type="submit">添加事实</Button>
        </form>
        <ul className="space-y-2">
          {facts.map((fact) => (
            <li key={fact.id} className="flex items-start justify-between gap-3 rounded-lg border bg-card p-3 text-sm">
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-medium">{fact.fact_type}</span>
                  <ConfidenceBadge confidence={fact.confidence} />
                  {fact.is_sensitive && (
                    <span className="rounded bg-destructive/10 px-1.5 py-0.5 text-xs text-destructive">敏感</span>
                  )}
                </div>
                <p className="mt-1">{fact.content}</p>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  if (window.confirm("确认删除这条事实？")) {
                    void deleteFact(fact.id).then(() => void load());
                  }
                }}
              >
                删除
              </Button>
            </li>
          ))}
          {facts.length === 0 && <li className="text-sm text-muted-foreground">暂无事实</li>}
        </ul>
      </section>

      <section className="space-y-3">
        <h2 className="text-lg font-medium">重要日期</h2>
        <form onSubmit={(e) => void addDate(e)} className="flex flex-wrap items-end gap-3 rounded-lg border bg-card p-4">
          <Field label="标题" className="flex-1">
            <TextInput value={dateTitle} onChange={(e) => setDateTitle(e.target.value)} placeholder="生日 / 纪念日" />
          </Field>
          <Field label="类型" className="w-32">
            <Select value={dateKind} onChange={(e) => setDateKind(e.target.value)}>
              <option value="birthday">生日</option>
              <option value="anniversary">纪念日</option>
              <option value="other">其他</option>
            </Select>
          </Field>
          <Field label="日期" className="w-44">
            <TextInput type="date" value={dateValue} onChange={(e) => setDateValue(e.target.value)} />
          </Field>
          <Button type="submit">添加</Button>
        </form>
        <ul className="space-y-2">
          {dates.map((item) => (
            <li key={item.id} className="flex items-center justify-between rounded-lg border bg-card p-3 text-sm">
              <span>
                {item.title} · {item.date_value}
              </span>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  if (window.confirm("确认删除这条日期？")) {
                    void deleteDate(item.id).then(() => void load());
                  }
                }}
              >
                删除
              </Button>
            </li>
          ))}
          {dates.length === 0 && <li className="text-sm text-muted-foreground">暂无重要日期</li>}
        </ul>
      </section>

      <section className="space-y-3">
        <h2 className="text-lg font-medium">待跟进</h2>
        <form onSubmit={(e) => void addFollowUp(e)} className="flex gap-3 rounded-lg border bg-card p-4">
          <TextInput
            placeholder="如：下周问问他新工作进展"
            value={followUpTitle}
            onChange={(e) => setFollowUpTitle(e.target.value)}
          />
          <Button type="submit">添加</Button>
        </form>
        <ul className="space-y-2">
          {followUps.map((task) => (
            <li key={task.id} className="flex items-center justify-between gap-3 rounded-lg border bg-card p-3 text-sm">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={task.completed}
                  onChange={() => void toggleFollowUp(task)}
                />
                <span className={task.completed ? "text-muted-foreground line-through" : undefined}>
                  {task.title}
                </span>
              </label>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  if (window.confirm("确认删除这条跟进？")) {
                    void deleteFollowUp(task.id).then(() => void load());
                  }
                }}
              >
                删除
              </Button>
            </li>
          ))}
          {followUps.length === 0 && <li className="text-sm text-muted-foreground">暂无待跟进事项</li>}
        </ul>
      </section>

      <section className="space-y-3">
        <h2 className="text-lg font-medium">自定义字段</h2>
        <div className="grid grid-cols-1 gap-3 rounded-lg border bg-card p-4 md:grid-cols-2">
          {customFields.map((field) => (
            <label key={field.id} className="space-y-1">
              <span className="text-sm text-muted-foreground">{field.name}</span>
              <TextInput
                defaultValue={String(customValues[field.id] ?? "")}
                onBlur={(e) => void saveCustomValue(field.id, e.target.value)}
              />
            </label>
          ))}
          {customFields.length === 0 && (
            <p className="text-sm text-muted-foreground">暂无自定义字段（可在设置页创建）</p>
          )}
        </div>
      </section>

      <section className="space-y-3">
        <h2 className="text-lg font-medium">时间线</h2>
        <ul className="space-y-2">
          {timeline.map((item) => (
            <li key={`${item.type}-${item.id}`} className="rounded-lg border bg-card p-3 text-sm">
              <div className="flex flex-wrap items-center gap-2">
                <span className="rounded bg-secondary px-2 py-0.5 text-xs text-secondary-foreground">
                  {item.type === "interaction" ? "互动" : item.type === "fact" ? "事实" : "重要日期"}
                </span>
                <span className="font-medium">{item.title}</span>
                <span className="text-xs text-muted-foreground">{formatDateTime(item.occurred_at)}</span>
              </div>
              {item.summary && <p className="mt-1 text-muted-foreground">{item.summary}</p>}
            </li>
          ))}
          {timeline.length === 0 && <li className="text-sm text-muted-foreground">时间线为空</li>}
        </ul>
      </section>
    </main>
  );
}
