import { useCallback, useEffect, useState, type FormEvent } from "react";
import {
  createBackup,
  downloadBackupUrl,
  exportJson,
  importJson,
  listBackups,
  restoreBackup,
  type BackupRecord,
} from "@/api/backup";
import {
  createModel,
  createProvider,
  deleteModel,
  deleteProvider,
  listModels,
  listProviders,
  syncModels,
  testProvider,
  updateModel,
  updateProvider,
} from "@/api/providers";
import type { AIModel, Provider } from "@/api/types";
import { Button } from "@/components/ui/button";
import { ErrorText, Field, Select, TextInput } from "@/components/ui/field";
import {
  createCustomField,
  deleteCustomField,
  listCustomFields,
} from "@/api/custom-fields";
import type { CustomField } from "@/api/types";

export function ProvidersPage() {
  const [providers, setProviders] = useState<Provider[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [models, setModels] = useState<AIModel[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [testResult, setTestResult] = useState<string | null>(null);
  const [syncResult, setSyncResult] = useState<string | null>(null);
  const [newModelId, setNewModelId] = useState("");
  // 备份区
  const [backups, setBackups] = useState<BackupRecord[]>([]);
  const [backupError, setBackupError] = useState<string | null>(null);
  const [backupStatus, setBackupStatus] = useState("");
  // 自定义字段定义
  const [customFields, setCustomFields] = useState<CustomField[]>([]);
  const [newFieldName, setNewFieldName] = useState("");
  const [newFieldType, setNewFieldType] = useState("text");

  // 新建/编辑表单
  const [form, setForm] = useState({
    name: "",
    provider_type: "deepseek",
    base_url: "",
    api_key: "",
    enabled: true,
    timeout_seconds: "60",
    max_retries: "2",
    proxy: "",
  });
  const [editingId, setEditingId] = useState<string | null>(null);

  const loadProviders = useCallback(async () => {
    try {
      const data = await listProviders();
      setProviders(data.items);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "加载失败");
    }
  }, []);

  const loadBackups = useCallback(async () => {
    try {
      setBackups(await listBackups());
    } catch (e) {
      setBackupError(e instanceof Error ? e.message : "加载备份失败");
    }
  }, []);

  const loadModels = useCallback(async (providerId: string) => {
    try {
      setModels(await listModels(providerId));
    } catch (e) {
      setError(e instanceof Error ? e.message : "加载模型失败");
    }
  }, []);

  useEffect(() => {
    void loadProviders();
    void loadBackups();
    void listCustomFields()
      .then(setCustomFields)
      .catch(() => undefined);
  }, [loadProviders, loadBackups]);

  const addCustomField = async () => {
    if (!newFieldName.trim()) {
      return;
    }
    try {
      await createCustomField({
        field_type: newFieldType,
        name: newFieldName.trim(),
      });
      setNewFieldName("");
      setCustomFields(await listCustomFields());
    } catch (e) {
      setError(e instanceof Error ? e.message : "创建字段失败");
    }
  };

  const removeCustomField = async (field: CustomField) => {
    if (!window.confirm(`确认删除自定义字段「${field.name}」？`)) {
      return;
    }
    await deleteCustomField(field.id);
    setCustomFields(await listCustomFields());
  };

  useEffect(() => {
    if (selectedId) {
      void loadModels(selectedId);
    }
  }, [selectedId, loadModels]);

  const selectProvider = (provider: Provider) => {
    setSelectedId(provider.id);
    setEditingId(provider.id);
    setForm({
      name: provider.name,
      provider_type: provider.provider_type,
      base_url: provider.base_url ?? "",
      api_key: "",
      enabled: provider.enabled,
      timeout_seconds: String(provider.timeout_seconds),
      max_retries: String(provider.max_retries),
      proxy: provider.proxy ?? "",
    });
    setTestResult(null);
    setSyncResult(null);
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!form.name.trim()) {
      setError("名称不能为空");
      return;
    }
    const payload = {
      name: form.name.trim(),
      provider_type: form.provider_type,
      base_url: form.base_url || null,
      api_key: form.api_key || null,
      enabled: form.enabled,
      timeout_seconds: Number(form.timeout_seconds) || 60,
      max_retries: Number(form.max_retries) || 2,
      proxy: form.proxy || null,
    };
    try {
      if (editingId) {
        await updateProvider(editingId, payload);
      } else {
        await createProvider(payload);
      }
      setForm({ ...form, name: "", api_key: "", base_url: "", proxy: "" });
      setEditingId(null);
      setSelectedId("");
      void loadProviders();
    } catch (e) {
      setError(e instanceof Error ? e.message : "保存失败");
    }
  };

  const handleTest = async () => {
    if (!selectedId) {
      return;
    }
    try {
      const result = await testProvider(selectedId);
      setTestResult(`连接成功：${result.models} 个模型，${result.latency_ms}ms`);
    } catch (e) {
      setTestResult(e instanceof Error ? `连接失败：${e.message}` : "连接失败");
    }
  };

  const handleSync = async () => {
    if (!selectedId) {
      return;
    }
    try {
      const result = await syncModels(selectedId);
      setSyncResult(`同步完成：新增 ${result.created}，更新 ${result.updated}`);
      void loadModels(selectedId);
    } catch (e) {
      setSyncResult(e instanceof Error ? `同步失败：${e.message}` : "同步失败");
    }
  };

  const addModel = async (e: FormEvent) => {
    e.preventDefault();
    if (!selectedId || !newModelId.trim()) {
      return;
    }
    try {
      await createModel(selectedId, { model_id: newModelId.trim() });
      setNewModelId("");
      void loadModels(selectedId);
    } catch (e) {
      setError(e instanceof Error ? e.message : "添加模型失败");
    }
  };

  const toggleModel = async (model: AIModel) => {
    try {
      await updateModel(model.id, { enabled: !model.enabled });
      void loadModels(selectedId);
    } catch (e) {
      setError(e instanceof Error ? e.message : "更新模型失败");
    }
  };

  const removeModel = async (model: AIModel) => {
    if (!window.confirm(`确认删除模型「${model.model_id}」？`)) {
      return;
    }
    await deleteModel(model.id);
    void loadModels(selectedId);
  };

  const removeProvider = async (provider: Provider) => {
    if (!window.confirm(`确认删除提供商「${provider.name}」？`)) {
      return;
    }
    await deleteProvider(provider.id);
    if (selectedId === provider.id) {
      setSelectedId("");
      setEditingId(null);
      setModels([]);
    }
    void loadProviders();
  };

  const handleExportJson = async () => {
    try {
      const data = await exportJson();
      const blob = new Blob([JSON.stringify(data, null, 2)], {
        type: "application/json",
      });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `socialization-export-${new Date().toISOString().slice(0, 10)}.json`;
      link.click();
      URL.revokeObjectURL(url);
      setBackupStatus("JSON 已导出");
    } catch (e) {
      setBackupError(e instanceof Error ? e.message : "导出失败");
    }
  };

  const handleImportJson = async (file: File) => {
    try {
      const text = await file.text();
      const payload = JSON.parse(text) as Record<string, unknown>;
      const result = await importJson(payload);
      const total = Object.values(result.imported).reduce((sum, n) => sum + n, 0);
      setBackupStatus(`导入完成：共 ${total} 条记录`);
      void loadBackups();
      window.location.reload();
    } catch (e) {
      setBackupError(e instanceof Error ? e.message : "导入失败");
    }
  };

  const handleCreateBackup = async () => {
    try {
      const record = await createBackup();
      setBackupStatus(`备份已创建：${record.filename}`);
      void loadBackups();
    } catch (e) {
      setBackupError(e instanceof Error ? e.message : "备份失败");
    }
  };

  const handleRestore = async (backup: BackupRecord) => {
    if (!window.confirm(`确认从「${backup.filename}」恢复？恢复前会自动生成安全快照。`)) {
      return;
    }
    try {
      const result = await restoreBackup(backup.id);
      setBackupStatus(`恢复完成（${result.restored_from}），安全快照：${result.safety_snapshot}`);
      window.location.reload();
    } catch (e) {
      setBackupError(e instanceof Error ? e.message : "恢复失败");
    }
  };

  return (
    <main className="mx-auto w-full max-w-5xl space-y-6 px-6 py-10">
      <h1 className="text-2xl font-semibold tracking-tight">AI 提供商设置</h1>
      <ErrorText message={error} />

      <section className="space-y-3">
        <h2 className="text-lg font-medium">{editingId ? "编辑提供商" : "新建提供商"}</h2>
        <form onSubmit={(e) => void handleSubmit(e)} className="grid grid-cols-1 gap-4 rounded-lg border bg-card p-4 md:grid-cols-2">
          <Field label="名称 *">
            <TextInput value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          </Field>
          <Field label="类型">
            <Select
              value={form.provider_type}
              onChange={(e) => setForm({ ...form, provider_type: e.target.value })}
            >
              <option value="deepseek">DeepSeek</option>
              <option value="openai">OpenAI</option>
              <option value="openai_compatible">OpenAI 兼容接口</option>
            </Select>
          </Field>
          <Field label="Base URL" className="md:col-span-2">
            <TextInput
              placeholder="留空使用类型默认地址"
              value={form.base_url}
              onChange={(e) => setForm({ ...form, base_url: e.target.value })}
            />
          </Field>
          <Field label={editingId ? "API Key（留空不修改）" : "API Key"}>
            <TextInput
              type="password"
              placeholder={editingId ? "已加密保存" : ""}
              value={form.api_key}
              onChange={(e) => setForm({ ...form, api_key: e.target.value })}
            />
          </Field>
          <Field label="代理（可选）">
            <TextInput value={form.proxy} onChange={(e) => setForm({ ...form, proxy: e.target.value })} />
          </Field>
          <Field label="超时（秒）">
            <TextInput
              type="number"
              value={form.timeout_seconds}
              onChange={(e) => setForm({ ...form, timeout_seconds: e.target.value })}
            />
          </Field>
          <Field label="重试次数">
            <TextInput
              type="number"
              value={form.max_retries}
              onChange={(e) => setForm({ ...form, max_retries: e.target.value })}
            />
          </Field>
          <label className="flex items-center gap-2 text-sm md:col-span-2">
            <input type="checkbox" checked={form.enabled} onChange={(e) => setForm({ ...form, enabled: e.target.checked })} />
            启用
          </label>
          <div className="flex gap-3 md:col-span-2">
            <Button type="submit">{editingId ? "保存修改" : "创建"}</Button>
            {editingId && (
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  setEditingId(null);
                  setForm({
                    name: "",
                    provider_type: "deepseek",
                    base_url: "",
                    api_key: "",
                    enabled: true,
                    timeout_seconds: "60",
                    max_retries: "2",
                    proxy: "",
                  });
                }}
              >
                取消编辑
              </Button>
            )}
          </div>
        </form>
      </section>

      <section className="space-y-3">
        <h2 className="text-lg font-medium">提供商列表</h2>
        {providers.length === 0 ? (
          <p className="text-muted-foreground">尚未配置提供商</p>
        ) : (
          <ul className="grid grid-cols-1 gap-3 md:grid-cols-2">
            {providers.map((provider) => (
              <li key={provider.id} className="rounded-lg border bg-card p-4 text-card-foreground shadow-sm">
                <div className="flex items-start justify-between">
                  <button
                    type="button"
                    onClick={() => selectProvider(provider)}
                    className="text-left"
                  >
                    <span className="font-medium">{provider.name}</span>
                    <span className="ml-2 rounded bg-secondary px-1.5 py-0.5 text-xs">{provider.provider_type}</span>
                    {!provider.enabled && <span className="ml-2 text-xs text-muted-foreground">已停用</span>}
                    <p className="mt-1 text-xs text-muted-foreground">
                      {provider.has_api_key ? `API Key 已配置（••••${provider.key_hint ?? ""}）` : "未配置 API Key"}
                    </p>
                  </button>
                  <Button variant="ghost" size="sm" onClick={() => void removeProvider(provider)}>
                    删除
                  </Button>
                </div>
                {selectedId === provider.id && (
                  <div className="mt-3 space-y-2">
                    <div className="flex flex-wrap gap-2">
                      <Button variant="outline" size="sm" onClick={() => void handleTest()}>
                        测试连接
                      </Button>
                      <Button variant="outline" size="sm" onClick={() => void handleSync()}>
                        同步模型
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => void updateProvider(provider.id, { clear_api_key: true }).then(() => void loadProviders())}
                      >
                        清除密钥
                      </Button>
                    </div>
                    {testResult && <p className="text-sm text-muted-foreground">{testResult}</p>}
                    {syncResult && <p className="text-sm text-muted-foreground">{syncResult}</p>}

                    <div className="space-y-2">
                      <h3 className="text-sm font-medium">模型</h3>
                      <ul className="space-y-1">
                        {models.map((model) => (
                          <li key={model.id} className="flex items-center justify-between rounded border px-2 py-1 text-sm">
                            <span>
                              {model.model_id}
                              {model.source === "sync" && (
                                <span className="ml-1 text-xs text-muted-foreground">（同步）</span>
                              )}
                            </span>
                            <span className="flex gap-2">
                              <label className="flex items-center gap-1 text-xs">
                                <input type="checkbox" checked={model.enabled} onChange={() => void toggleModel(model)} />
                                启用
                              </label>
                              <Button variant="ghost" size="sm" onClick={() => void removeModel(model)}>
                                删
                              </Button>
                            </span>
                          </li>
                        ))}
                      </ul>
                      <form onSubmit={(e) => void addModel(e)} className="flex gap-2">
                        <TextInput
                          placeholder="手动添加模型 ID"
                          value={newModelId}
                          onChange={(e) => setNewModelId(e.target.value)}
                        />
                        <Button type="submit" variant="outline" size="sm">
                          添加
                        </Button>
                      </form>
                    </div>
                  </div>
                )}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="space-y-3">
        <h2 className="text-lg font-medium">数据备份</h2>
        <div className="flex flex-wrap gap-3 rounded-lg border bg-card p-4">
          <Button variant="outline" onClick={() => void handleExportJson()}>
            导出 JSON
          </Button>
          <label className="inline-flex cursor-pointer items-center justify-center rounded-md border border-input bg-background px-4 py-2 text-sm shadow-sm hover:bg-accent">
            导入 JSON
            <input
              type="file"
              accept="application/json,.json"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) {
                  void handleImportJson(file);
                }
                e.target.value = "";
              }}
            />
          </label>
          <Button onClick={() => void handleCreateBackup()}>创建备份</Button>
          {backupStatus && <span className="self-center text-sm text-muted-foreground">{backupStatus}</span>}
        </div>
        {backupError && <p className="text-sm text-destructive">{backupError}</p>}
        {backups.length > 0 && (
          <ul className="space-y-2">
            {backups.map((backup) => (
              <li key={backup.id} className="flex items-center justify-between rounded-lg border bg-card p-3 text-sm">
                <span>
                  {backup.filename}（{(backup.size_bytes / 1024).toFixed(1)} KB ·{" "}
                  {new Date(backup.created_at).toLocaleString("zh-CN", { hour12: false })}）
                </span>
                <span className="flex gap-2">
                  <a className="text-primary underline" href={downloadBackupUrl(backup.id)} download>
                    下载
                  </a>
                  <button type="button" className="text-destructive underline" onClick={() => void handleRestore(backup)}>
                    恢复
                  </button>
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="space-y-3">
        <h2 className="text-lg font-medium">自定义字段定义</h2>
        <div className="flex flex-wrap gap-2 rounded-lg border bg-card p-4">
          <TextInput
            className="w-56"
            placeholder="字段名，如：喜欢的咖啡"
            value={newFieldName}
            onChange={(e) => setNewFieldName(e.target.value)}
          />
          <Select
            className="w-40"
            value={newFieldType}
            onChange={(e) => setNewFieldType(e.target.value)}
          >
            <option value="text">单行文本</option>
            <option value="textarea">多行文本</option>
            <option value="number">数字</option>
            <option value="date">日期</option>
            <option value="link">链接</option>
            <option value="boolean">布尔</option>
          </Select>
          <Button variant="outline" onClick={() => void addCustomField()}>
            添加字段
          </Button>
        </div>
        <ul className="flex flex-wrap gap-2">
          {customFields.map((field) => (
            <li key={field.id} className="flex items-center gap-2 rounded border px-2.5 py-1 text-sm">
              {field.name}
              <Button variant="ghost" size="sm" onClick={() => void removeCustomField(field)}>
                删
              </Button>
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}
