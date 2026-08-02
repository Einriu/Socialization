import { useEffect, useState, type FormEvent } from "react";
import { createPerson, getPerson, updatePerson } from "@/api/persons";
import type { PersonInput } from "@/api/types";
import { Button } from "@/components/ui/button";
import { ErrorText, Field, Select, TextArea, TextInput } from "@/components/ui/field";
import { fromLocalInputValue, toLocalInputValue } from "@/lib/datetime";
import { matchRoute, useRouter } from "@/lib/router";

interface FormState {
  name: string;
  nickname: string;
  relationship_type: string;
  familiarity_level: string;
  met_at: string;
  met_location: string;
  met_via: string;
  organization: string;
  occupation: string;
  location: string;
  summary: string;
  privacy_level: string;
}

const EMPTY: FormState = {
  name: "",
  nickname: "",
  relationship_type: "",
  familiarity_level: "1",
  met_at: "",
  met_location: "",
  met_via: "",
  organization: "",
  occupation: "",
  location: "",
  summary: "",
  privacy_level: "private",
};

export function PersonFormPage() {
  const { path, navigate } = useRouter();
  const editMatch = matchRoute(path, "/persons/:id/edit");
  const personId = editMatch?.params.id;
  const isEdit = personId !== undefined;

  const [form, setForm] = useState<FormState>(EMPTY);
  const [loading, setLoading] = useState(isEdit);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!personId) {
      return;
    }
    void getPerson(personId)
      .then((person) => {
        setForm({
          name: person.name,
          nickname: person.nickname ?? "",
          relationship_type: person.relationship_type ?? "",
          familiarity_level: String(person.familiarity_level),
          met_at: toLocalInputValue(person.met_at),
          met_location: person.met_location ?? "",
          met_via: person.met_via ?? "",
          organization: person.organization ?? "",
          occupation: person.occupation ?? "",
          location: person.location ?? "",
          summary: person.summary ?? "",
          privacy_level: person.privacy_level,
        });
        setLoading(false);
      })
      .catch((e: unknown) => {
        setError(e instanceof Error ? e.message : "加载失败");
        setLoading(false);
      });
  }, [personId]);

  const setField = (key: keyof FormState, value: string) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!form.name.trim()) {
      setError("姓名不能为空");
      return;
    }
    setSaving(true);
    setError(null);
    const input: PersonInput = {
      name: form.name.trim(),
      nickname: form.nickname || null,
      relationship_type: form.relationship_type || null,
      familiarity_level: Number(form.familiarity_level) || 1,
      met_at: fromLocalInputValue(form.met_at),
      met_location: form.met_location || null,
      met_via: form.met_via || null,
      organization: form.organization || null,
      occupation: form.occupation || null,
      location: form.location || null,
      summary: form.summary || null,
      privacy_level: form.privacy_level,
    };
    try {
      const saved = personId
        ? await updatePerson(personId, input)
        : await createPerson(input);
      navigate(`/persons/${saved.id}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "保存失败");
      setSaving(false);
    }
  };

  return (
    <main className="mx-auto w-full max-w-3xl space-y-6 px-6 py-10">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold tracking-tight">
          {isEdit ? "编辑人物" : "新建人物"}
        </h1>
        <Button variant="ghost" onClick={() => navigate(personId ? `/persons/${personId}` : "/persons")}>
          返回
        </Button>
      </div>

      {loading ? (
        <p className="text-muted-foreground">加载中…</p>
      ) : (
        <form onSubmit={(e) => void handleSubmit(e)} className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <Field label="姓名 *" className="md:col-span-2">
            <TextInput value={form.name} onChange={(e) => setField("name", e.target.value)} />
          </Field>
          <Field label="昵称">
            <TextInput value={form.nickname} onChange={(e) => setField("nickname", e.target.value)} />
          </Field>
          <Field label="关系类型">
            <TextInput
              placeholder="同事 / 同学 / 朋友 / 家人…"
              value={form.relationship_type}
              onChange={(e) => setField("relationship_type", e.target.value)}
            />
          </Field>
          <Field label="熟悉程度（1–6）">
            <TextInput
              type="number"
              min={1}
              max={6}
              value={form.familiarity_level}
              onChange={(e) => setField("familiarity_level", e.target.value)}
            />
          </Field>
          <Field label="认识时间">
            <TextInput
              type="datetime-local"
              value={form.met_at}
              onChange={(e) => setField("met_at", e.target.value)}
            />
          </Field>
          <Field label="认识地点">
            <TextInput value={form.met_location} onChange={(e) => setField("met_location", e.target.value)} />
          </Field>
          <Field label="认识途径">
            <TextInput value={form.met_via} onChange={(e) => setField("met_via", e.target.value)} />
          </Field>
          <Field label="公司 / 单位">
            <TextInput value={form.organization} onChange={(e) => setField("organization", e.target.value)} />
          </Field>
          <Field label="职业 / 职位">
            <TextInput value={form.occupation} onChange={(e) => setField("occupation", e.target.value)} />
          </Field>
          <Field label="所在地">
            <TextInput value={form.location} onChange={(e) => setField("location", e.target.value)} />
          </Field>
          <Field label="隐私等级">
            <Select value={form.privacy_level} onChange={(e) => setField("privacy_level", e.target.value)}>
              <option value="private">私密</option>
              <option value="protected">受保护</option>
              <option value="public">公开</option>
            </Select>
          </Field>
          <Field label="摘要" className="md:col-span-2">
            <TextArea value={form.summary} onChange={(e) => setField("summary", e.target.value)} />
          </Field>
          <ErrorText message={error} />
          <div className="flex gap-3 md:col-span-2">
            <Button type="submit" disabled={saving}>
              {saving ? "保存中…" : "保存"}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={() => navigate(personId ? `/persons/${personId}` : "/persons")}
            >
              取消
            </Button>
          </div>
        </form>
      )}
    </main>
  );
}
