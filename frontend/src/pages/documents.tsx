import { useCallback, useEffect, useState, type FormEvent } from "react";
import {
  deleteDocument,
  listChunks,
  listDocuments,
  processDocument,
  setDocumentLinks,
  uploadDocument,
} from "@/api/documents";
import { listPersons } from "@/api/persons";
import { listTopics } from "@/api/topics";
import type { DocumentChunkItem, DocumentRecord, Person, Topic } from "@/api/types";
import { Button } from "@/components/ui/button";
import { ErrorText, Select } from "@/components/ui/field";

const STATUS_LABELS: Record<string, string> = {
  pending: "等待处理",
  processing: "正在解析",
  completed: "已完成",
  partial_failed: "部分失败",
  failed: "解析失败",
};

export function DocumentsPage() {
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [persons, setPersons] = useState<Person[]>([]);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [chunks, setChunks] = useState<DocumentChunkItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [linkPerson, setLinkPerson] = useState("");
  const [linkTopic, setLinkTopic] = useState("");

  const load = useCallback(async () => {
    try {
      const [data, p, t] = await Promise.all([
        listDocuments({ pageSize: 50 }),
        listPersons({ pageSize: 100 }),
        listTopics({ pageSize: 100 }),
      ]);
      setDocuments(data.items);
      setPersons(p.items);
      setTopics(t.items);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "加载失败");
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const handleUpload = async (file: File) => {
    try {
      await uploadDocument(file);
      void load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "上传失败");
    }
  };

  const openDocument = async (document: DocumentRecord) => {
    setSelectedId(document.id);
    setLinkPerson(document.person_ids[0] ?? "");
    setLinkTopic(document.topic_ids[0] ?? "");
    try {
      const data = await listChunks(document.id);
      setChunks(data.items);
    } catch (e) {
      setError(e instanceof Error ? e.message : "加载切块失败");
    }
  };

  const applyLinks = async (e: FormEvent) => {
    e.preventDefault();
    if (!selectedId) {
      return;
    }
    try {
      await setDocumentLinks(selectedId, {
        person_id: linkPerson || null,
        topic_id: linkTopic || null,
      });
      void load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "关联失败");
    }
  };

  const handleProcess = async (document: DocumentRecord) => {
    try {
      await processDocument(document.id);
      void load();
      if (selectedId === document.id) {
        void openDocument(document);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "处理失败");
    }
  };

  const handleDelete = async (document: DocumentRecord) => {
    if (!window.confirm(`确认删除文件「${document.filename}」？`)) {
      return;
    }
    await deleteDocument(document.id);
    if (selectedId === document.id) {
      setSelectedId("");
      setChunks([]);
    }
    void load();
  };

  return (
    <main className="mx-auto w-full max-w-5xl space-y-6 px-6 py-10">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold tracking-tight">文件资料库</h1>
        <label className="inline-flex cursor-pointer items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow hover:bg-primary/90">
          上传文件
          <input
            type="file"
            className="hidden"
            accept=".pdf,.docx,.pptx,.xlsx,.txt,.md,.html,.htm,.csv"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) {
                void handleUpload(file);
              }
              e.target.value = "";
            }}
          />
        </label>
      </div>
      <ErrorText message={error} />

      <div className="grid grid-cols-1 gap-6 md:grid-cols-[1fr_1.2fr]">
        <ul className="space-y-2">
          {documents.map((document) => (
            <li key={document.id} className="rounded-lg border bg-card p-3 text-sm shadow-sm">
              <div className="flex items-start justify-between gap-2">
                <button type="button" className="text-left" onClick={() => void openDocument(document)}>
                  <span className="font-medium">{document.filename}</span>
                  <span className="ml-2 rounded bg-secondary px-1.5 py-0.5 text-xs">
                    {STATUS_LABELS[document.status] ?? document.status}
                  </span>
                  <p className="mt-1 text-xs text-muted-foreground">
                    {(document.file_size / 1024).toFixed(1)} KB · {document.chunk_count} 片段
                  </p>
                </button>
                <span className="flex gap-1">
                  {document.status !== "completed" && (
                    <Button variant="outline" size="sm" onClick={() => void handleProcess(document)}>
                      处理
                    </Button>
                  )}
                  <Button variant="ghost" size="sm" onClick={() => void handleDelete(document)}>
                    删
                  </Button>
                </span>
              </div>
              {document.error_message && (
                <p className="mt-1 text-xs text-destructive">{document.error_message}</p>
              )}
            </li>
          ))}
          {documents.length === 0 && <li className="text-sm text-muted-foreground">还没有文件</li>}
        </ul>

        <section className="space-y-3">
          {!selectedId ? (
            <p className="rounded-lg border bg-card p-8 text-center text-muted-foreground">
              选择一个文件查看切块与关联
            </p>
          ) : (
            <>
              <form onSubmit={(e) => void applyLinks(e)} className="flex flex-wrap items-end gap-2 rounded-lg border bg-card p-3">
                <Select className="w-44" value={linkPerson} onChange={(e) => setLinkPerson(e.target.value)} aria-label="关联人物">
                  <option value="">不关联人物</option>
                  {persons.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name}
                    </option>
                  ))}
                </Select>
                <Select className="w-44" value={linkTopic} onChange={(e) => setLinkTopic(e.target.value)} aria-label="关联话题">
                  <option value="">不关联话题</option>
                  {topics.map((t) => (
                    <option key={t.id} value={t.id}>
                      {t.name}
                    </option>
                  ))}
                </Select>
                <Button type="submit" variant="outline" size="sm">
                  应用关联
                </Button>
              </form>
              <h2 className="text-sm font-medium text-muted-foreground">切块（可被 AI 检索）</h2>
              <ul className="space-y-2">
                {chunks.map((chunk) => (
                  <li key={chunk.id} className="rounded-lg border bg-card p-3 text-sm">
                    <span className="text-xs text-muted-foreground">片段 {chunk.chunk_index}</span>
                    <p className="mt-1 line-clamp-3">{chunk.content}</p>
                  </li>
                ))}
                {chunks.length === 0 && (
                  <li className="text-sm text-muted-foreground">
                    暂无切块，点击“处理”解析文件
                  </li>
                )}
              </ul>
            </>
          )}
        </section>
      </div>
    </main>
  );
}
