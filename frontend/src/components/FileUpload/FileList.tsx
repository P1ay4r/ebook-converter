import { useState } from 'react';
import { Trash2, FileText, Download, ArrowLeftRight } from 'lucide-react';
import type { FileItem } from '../../types';
import { deleteFile, getDownloadUrl } from '../../api/files';

interface FileListProps {
  files: FileItem[];
  loading: boolean;
  onRefresh: () => void;
  onConvert: (fileIds: string[]) => void;
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function FileList({ files, loading, onRefresh, onConvert }: FileListProps) {
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [deleting, setDeleting] = useState<string | null>(null);

  const toggleSelect = (id: string) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const handleDelete = async (id: string) => {
    setDeleting(id);
    try {
      await deleteFile(id);
      onRefresh();
    } catch {
      // ignore
    }
    setDeleting(null);
  };

  const handleConvert = () => {
    if (selectedIds.size > 0) {
      onConvert(Array.from(selectedIds));
    }
  };

  if (loading) {
    return (
      <div className="card p-6 text-center text-gray-500">
        加载中...
      </div>
    );
  }

  if (files.length === 0) {
    return null;
  }

  return (
    <div className="card overflow-hidden">
      <div className="p-4 border-b border-gray-100 flex items-center justify-between">
        <h2 className="font-semibold text-gray-800">已上传文件 ({files.length})</h2>
        <div className="flex gap-2">
          {selectedIds.size > 0 && (
            <>
              <span className="text-sm text-gray-500 self-center">
                已选 {selectedIds.size} 项
              </span>
              <button className="btn-primary text-sm" onClick={handleConvert}>
                <ArrowLeftRight className="h-4 w-4 mr-1" />
                转换
              </button>
            </>
          )}
        </div>
      </div>

      <div className="divide-y divide-gray-100">
        {files.map((file) => (
          <div
            key={file.id}
            className={`flex items-center gap-3 p-3 hover:bg-gray-50 transition-colors
              ${selectedIds.has(file.id) ? 'bg-primary-50' : ''}
            `}
          >
            <input
              type="checkbox"
              checked={selectedIds.has(file.id)}
              onChange={() => toggleSelect(file.id)}
              className="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />

            <FileText className="h-5 w-5 text-gray-400 shrink-0" />

            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-800 truncate">
                {file.filename}
              </p>
              <p className="text-xs text-gray-400">
                {file.format.toUpperCase()} · {formatSize(file.size)}
                <span className="ml-2">
                  {file.status === 'uploaded' ? '已上传' : file.status}
                </span>
              </p>
            </div>

            <a
              href={getDownloadUrl(file.id)}
              className="p-1.5 text-gray-400 hover:text-primary-600 transition-colors"
              title="下载"
            >
              <Download className="h-4 w-4" />
            </a>

            <button
              onClick={() => handleDelete(file.id)}
              disabled={deleting === file.id}
              className="p-1.5 text-gray-400 hover:text-red-600 transition-colors disabled:opacity-50"
              title="删除"
            >
              <Trash2 className="h-4 w-4" />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
