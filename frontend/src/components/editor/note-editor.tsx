import { useCallback, useEffect, useRef } from "react";
import Highlight from "@tiptap/extension-highlight";
import Image from "@tiptap/extension-image";
import { Table } from "@tiptap/extension-table";
import TableCell from "@tiptap/extension-table-cell";
import TableHeader from "@tiptap/extension-table-header";
import TableRow from "@tiptap/extension-table-row";
import TaskItem from "@tiptap/extension-task-item";
import TaskList from "@tiptap/extension-task-list";
import { EditorContent, useEditor } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import { Button } from "@/components/ui/button";

interface NoteEditorProps {
  initialJson: object | null;
  onSave: (json: object, plainText: string) => void;
}

const AUTOSAVE_DELAY_MS = 1500;

export function NoteEditor({ initialJson, onSave }: NoteEditorProps) {
  const onSaveRef = useRef(onSave);
  onSaveRef.current = onSave;

  const editor = useEditor({
    extensions: [
      StarterKit,
      Highlight,
      Image.configure({ allowBase64: true }),
      Table.configure({ resizable: true }),
      TableRow,
      TableHeader,
      TableCell,
      TaskList,
      TaskItem.configure({ nested: true }),
    ],
    content: initialJson ?? { type: "doc", content: [] },
  });

  const saveTimer = useRef<number | null>(null);

  useEffect(() => {
    if (!editor) {
      return;
    }
    const handleUpdate = () => {
      if (saveTimer.current !== null) {
        window.clearTimeout(saveTimer.current);
      }
      saveTimer.current = window.setTimeout(() => {
        const json = editor.getJSON();
        onSaveRef.current(json, editor.getText());
      }, AUTOSAVE_DELAY_MS);
    };
    editor.on("update", handleUpdate);
    return () => {
      editor.off("update", handleUpdate);
      if (saveTimer.current !== null) {
        window.clearTimeout(saveTimer.current);
      }
    };
  }, [editor]);

  const flushNow = useCallback(() => {
    if (editor && saveTimer.current !== null) {
      window.clearTimeout(saveTimer.current);
      saveTimer.current = null;
      onSaveRef.current(editor.getJSON(), editor.getText());
    }
  }, [editor]);

  useEffect(() => {
    const onBeforeUnload = () => {
      if (saveTimer.current !== null) {
        window.clearTimeout(saveTimer.current);
        saveTimer.current = null;
        if (editor) {
          onSaveRef.current(editor.getJSON(), editor.getText());
        }
      }
    };
    window.addEventListener("beforeunload", onBeforeUnload);
    return () => window.removeEventListener("beforeunload", onBeforeUnload);
  }, [editor]);

  if (!editor) {
    return <p className="text-muted-foreground">编辑器加载中…</p>;
  }

  const setLink = (url: string | null) => {
    if (url === null) {
      return;
    }
    editor.chain().focus().setImage({ src: url }).run();
  };

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap gap-1">
        <ToolbarButton active={editor.isActive("bold")} onClick={() => editor.chain().focus().toggleBold().run()}>
          加粗
        </ToolbarButton>
        <ToolbarButton active={editor.isActive("italic")} onClick={() => editor.chain().focus().toggleItalic().run()}>
          斜体
        </ToolbarButton>
        <ToolbarButton active={editor.isActive("highlight")} onClick={() => editor.chain().focus().toggleHighlight().run()}>
          高亮
        </ToolbarButton>
        <ToolbarButton active={editor.isActive("heading", { level: 1 })} onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}>
          H1
        </ToolbarButton>
        <ToolbarButton active={editor.isActive("heading", { level: 2 })} onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}>
          H2
        </ToolbarButton>
        <ToolbarButton active={editor.isActive("bulletList")} onClick={() => editor.chain().focus().toggleBulletList().run()}>
          列表
        </ToolbarButton>
        <ToolbarButton active={editor.isActive("orderedList")} onClick={() => editor.chain().focus().toggleOrderedList().run()}>
          编号
        </ToolbarButton>
        <ToolbarButton active={editor.isActive("taskList")} onClick={() => editor.chain().focus().toggleTaskList().run()}>
          待办
        </ToolbarButton>
        <ToolbarButton active={editor.isActive("blockquote")} onClick={() => editor.chain().focus().toggleBlockquote().run()}>
          引用
        </ToolbarButton>
        <ToolbarButton active={editor.isActive("codeBlock")} onClick={() => editor.chain().focus().toggleCodeBlock().run()}>
          代码
        </ToolbarButton>
        <ToolbarButton
          onClick={() => {
            const url = window.prompt("图片地址");
            setLink(url);
          }}
        >
          图片
        </ToolbarButton>
        <ToolbarButton
          onClick={() => {
            editor.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run();
          }}
        >
          表格
        </ToolbarButton>
        <Button variant="ghost" size="sm" onClick={() => editor.chain().focus().undo().run()}>
          撤销
        </Button>
        <Button variant="ghost" size="sm" onClick={() => editor.chain().focus().redo().run()}>
          重做
        </Button>
        <Button variant="outline" size="sm" onClick={flushNow}>
          立即保存
        </Button>
      </div>
      <div className="min-h-80 rounded-lg border bg-card p-4">
        <EditorContent editor={editor} />
      </div>
    </div>
  );
}

function ToolbarButton({
  active,
  onClick,
  children,
}: {
  active?: boolean;
  onClick: () => void;
  children: string;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`rounded px-2 py-1 text-sm ${
        active ? "bg-secondary font-medium text-secondary-foreground" : "text-muted-foreground hover:text-foreground"
      }`}
    >
      {children}
    </button>
  );
}
