import { useEffect, useState, type FormEvent } from "react";
import { createInteraction, updateInteraction } from "@/api/interactions";
import { listPersons } from "@/api/persons";
import type { InteractionInput, Person } from "@/api/types";
import { Button } from "@/components/ui/button";
import { ErrorText, Field, Select, TextArea, TextInput } from "@/components/ui/field";
import { fromLocalInputValue, toLocalInputValue } from "@/lib/datetime";
import { matchRoute, useRouter } from "@/lib/router";

interface FormState {
  title: string;
  occurred_at: string;
  location: string;
  interaction_type: string;
  duration_minutes: string;
  summary: string;
  new_info: string;
  mood_state: string;
  my_performance: string;
  positive_feedback: string;
  awkward_points: string;
  follow_up: string;
  privacy_level: string;
  participant_ids: string[];
}

const EMPTY: FormState = {
  title: "",
  occurred_at: "",
  location: "",
  interaction_type: "face_to_face",
  duration_minutes: "",
  summary: "",
  new_info: "",
  mood_state: "",
  my_performance: "",
  positive_feedback: "",
  awkward_points: "",
  follow_up: "",
  privacy_level: "private",
  participant_ids: [],
};

export function InteractionFormPage() {
  const { path, navigate } = useRouter();
  const editMatch = matchRoute(path, "/interactions/:id/edit");
  const interactionId = editMatch?.params.id;
  const isEdit = interactionId !== undefined;

  const [form, setForm] = useState<FormState>(EMPTY);
  const [persons, setPersons] = useState<Person[]>([]);
  const [loading, setLoading] = useState(isEdit);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void listPersons({ pageSize: 100 })
      .then((data) => setPersons(data.items))
      .catch(() => undefined);
  }, []);

  // 编辑时加载既有互动（避免依赖循环，直接 fetch）
  useEffect(() => {
    if (!interactionId) {
      return;
    }
    void fetch(`/api/interactions/${interactionId}`)
      .then((resp) => resp.json())
      .then((body) => {
        const item = body.data;
        setForm({
          title: item.title,
          occurred_at: toLocalInputValue(item.occurred_at),
          location: item.location ?? "",
          interaction_type: item.interaction_type,
          duration_minutes: item.duration_minutes == null ? "" : String(item.duration_minutes),
          summary: item.summary ?? "",
          new_info: item.new_info ?? "",
          mood_state: item.mood_state ?? "",
          my_performance: item.my_performance ?? "",
          positive_feedback: item.positive_feedback ?? "",
          awkward_points: item.awkward_points ?? "",
          follow_up: item.follow_up ?? "",
          privacy_level: item.privacy_level,
          participant_ids: item.persons.map((p: { id: string }) => p.id),
        });
        setLoading(false);
      })
      .catch((e: unknown) => {
        setError(e instanceof Error ? e.message : "加载失败");
        setLoading(false);
      });
  }, [interactionId]);

  const setField = (key: keyof FormState, value: string | string[]) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const toggleParticipant = (id: string) => {
    const current = new Set(form.participant_ids);
    if (current.has(id)) {
      current.delete(id);
    } else {
      current.add(id);
    }
    setField("participant_ids", [...current]);
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!form.title.trim()) {
      setError("标题不能为空");
      return;
    }
    if (form.participant_ids.length === 0) {
      setError("请至少选择一位关联人物");
      return;
    }
    setSaving(true);
    setError(null);
    const input: InteractionInput = {
      title: form.title.trim(),
      occurred_at: fromLocalInputValue(form.occurred_at),
      location: form.location || null,
      interaction_type: form.interaction_type,
      duration_minutes: form.duration_minutes ? Number(form.duration_minutes) : null,
      summary: form.summary || null,
      new_info: form.new_info || null,
      mood_state: form.mood_state || null,
      my_performance: form.my_performance || null,
      positive_feedback: form.positive_feedback || null,
      awkward_points: form.awkward_points || null,
      follow_up: form.follow_up || null,
      privacy_level: form.privacy_level,
      participant_ids: form.participant_ids,
    };
    try {
      if (interactionId) {
        await updateInteraction(interactionId, input);
      } else {
        await createInteraction(input);
      }
      navigate("/interactions");
    } catch (e) {
      setError(e instanceof Error ? e.message : "保存失败");
      setSaving(false);
    }
  };

  return (
    <main className="mx-auto w-full max-w-3xl space-y-6 px-6 py-10">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold tracking-tight">
          {isEdit ? "编辑互动" : "记录互动"}
        </h1>
        <Button variant="ghost" onClick={() => navigate("/interactions")}>
          返回
        </Button>
      </div>

      {loading ? (
        <p className="text-muted-foreground">加载中…</p>
      ) : (
        <form onSubmit={(e) => void handleSubmit(e)} className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <Field label="标题 *" className="md:col-span-2">
            <TextInput value={form.title} onChange={(e) => setField("title", e.target.value)} />
          </Field>
          <Field label="时间">
            <TextInput
              type="datetime-local"
              value={form.occurred_at}
              onChange={(e) => setField("occurred_at", e.target.value)}
            />
          </Field>
          <Field label="互动方式">
            <Select
              value={form.interaction_type}
              onChange={(e) => setField("interaction_type", e.target.value)}
            >
              <option value="face_to_face">面对面聊天</option>
              <option value="phone">电话</option>
              <option value="wechat">微信聊天</option>
              <option value="party">聚会</option>
              <option value="work">工作交流</option>
              <option value="sports">一起运动</option>
              <option value="meal">一起吃饭</option>
              <option value="other">其他</option>
            </Select>
          </Field>
          <Field label="地点">
            <TextInput value={form.location} onChange={(e) => setField("location", e.target.value)} />
          </Field>
          <Field label="时长（分钟）">
            <TextInput
              type="number"
              min={0}
              value={form.duration_minutes}
              onChange={(e) => setField("duration_minutes", e.target.value)}
            />
          </Field>
          <Field label="隐私等级">
            <Select
              value={form.privacy_level}
              onChange={(e) => setField("privacy_level", e.target.value)}
            >
              <option value="private">私密</option>
              <option value="protected">受保护</option>
              <option value="public">公开</option>
            </Select>
          </Field>
          <Field label="互动摘要" className="md:col-span-2">
            <TextArea value={form.summary} onChange={(e) => setField("summary", e.target.value)} />
          </Field>
          <Field label="对方新增信息" className="md:col-span-2">
            <TextArea value={form.new_info} onChange={(e) => setField("new_info", e.target.value)} />
          </Field>
          <Field label="对方情绪或状态">
            <TextInput value={form.mood_state} onChange={(e) => setField("mood_state", e.target.value)} />
          </Field>
          <Field label="自己的表现">
            <TextInput value={form.my_performance} onChange={(e) => setField("my_performance", e.target.value)} />
          </Field>
          <Field label="正面反馈">
            <TextInput
              value={form.positive_feedback}
              onChange={(e) => setField("positive_feedback", e.target.value)}
            />
          </Field>
          <Field label="冷场或问题">
            <TextInput
              value={form.awkward_points}
              onChange={(e) => setField("awkward_points", e.target.value)}
            />
          </Field>
          <Field label="后续事项（自动生成跟进）" className="md:col-span-2">
            <TextInput value={form.follow_up} onChange={(e) => setField("follow_up", e.target.value)} />
          </Field>

          <fieldset className="space-y-2 md:col-span-2">
            <legend className="text-sm font-medium text-muted-foreground">关联人物 *</legend>
            <div className="grid grid-cols-2 gap-2 md:grid-cols-3">
              {persons.map((person) => (
                <label key={person.id} className="flex items-center gap-2 rounded border px-3 py-2 text-sm">
                  <input
                    type="checkbox"
                    checked={form.participant_ids.includes(person.id)}
                    onChange={() => toggleParticipant(person.id)}
                  />
                  {person.name}
                </label>
              ))}
            </div>
            {persons.length === 0 && (
              <p className="text-sm text-muted-foreground">请先创建人物，再记录互动。</p>
            )}
          </fieldset>

          <ErrorText message={error} />
          <div className="flex gap-3 md:col-span-2">
            <Button type="submit" disabled={saving}>
              {saving ? "保存中…" : "保存"}
            </Button>
            <Button type="button" variant="outline" onClick={() => navigate("/interactions")}>
              取消
            </Button>
          </div>
        </form>
      )}
    </main>
  );
}
