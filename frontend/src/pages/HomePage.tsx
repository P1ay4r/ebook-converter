import { useState, useEffect, useCallback } from 'react';
import { BookOpen } from 'lucide-react';
import { DropZone } from '../components/FileUpload/DropZone';
import { FileList } from '../components/FileUpload/FileList';
import { FormatSelector } from '../components/Conversion/FormatSelector';
import { OptionPanel } from '../components/Conversion/OptionPanel';
import { ProgressBar } from '../components/Conversion/ProgressBar';
import { MetadataEditor } from '../components/Metadata/MetadataEditor';
import { useWebSocket } from '../hooks/useWebSocket';
import { uploadFile, listFiles, getFormats } from '../api/files';
import { startConversion, getTask } from '../api/conversion';
import type {
  FileItem,
  FormatsResponse,
  ConversionOptions,
  TaskResponse,
  WSProgressMessage,
} from '../types';

export function HomePage() {
  // 文件列表
  const [files, setFiles] = useState<FileItem[]>([]);
  const [filesLoading, setFilesLoading] = useState(true);

  // 上传状态
  const [uploading, setUploading] = useState(false);

  // 格式信息
  const [formats, setFormats] = useState<FormatsResponse | null>(null);

  // 转换对话框
  const [showConvert, setShowConvert] = useState(false);
  const [convertFileIds, setConvertFileIds] = useState<string[]>([]);
  const [targetFormat, setTargetFormat] = useState('');
  const [options, setOptions] = useState<ConversionOptions>({});

  // 转换任务
  const [tasks, setTasks] = useState<TaskResponse[]>([]);
  const [batchId, setBatchId] = useState<string | null>(null);

  // 元数据编辑
  const [editingFileId, setEditingFileId] = useState<string | null>(null);

  // 加载文件列表
  const loadFiles = useCallback(async () => {
    setFilesLoading(true);
    try {
      const resp = await listFiles(1, 50);
      setFiles(resp.items);
    } catch {
      // ignore
    }
    setFilesLoading(false);
  }, []);

  // 加载格式信息
  useEffect(() => {
    getFormats().then(setFormats).catch(() => {});
    loadFiles();
  }, [loadFiles]);

  // 文件上传
  const handleFilesSelected = async (selectedFiles: File[]) => {
    setUploading(true);
    for (const file of selectedFiles) {
      try {
        await uploadFile(file);
      } catch {
        // ignore individual failures
      }
    }
    setUploading(false);
    loadFiles();
  };

  // 打开转换对话框
  const handleConvert = (fileIds: string[]) => {
    setConvertFileIds(fileIds);
    setTargetFormat('');
    setOptions({});
    setShowConvert(true);
    setTasks([]);
    setBatchId(null);
  };

  // 执行转换
  const handleStartConversion = async () => {
    if (!targetFormat || convertFileIds.length === 0) return;

    try {
      const result = await startConversion({
        file_ids: convertFileIds,
        target_format: targetFormat,
        options: Object.keys(options).length > 0 ? options : undefined,
      });
      setBatchId(result.batch_id);
      setTasks(result.tasks);
      setShowConvert(false);
    } catch (e: any) {
      alert(e.message || '转换启动失败');
    }
  };

  // WebSocket 监听
  const activeTaskId = tasks.find((t) => t.status === 'processing' || t.status === 'pending')?.task_id || null;

  useWebSocket(activeTaskId, (msg: WSProgressMessage) => {
    setTasks((prev) =>
      prev.map((t) =>
        t.task_id === msg.task_id
          ? { ...t, status: msg.status, progress: msg.progress }
          : t
      )
    );
  });

  // 轮询任务状态（兜底）
  useEffect(() => {
    if (!batchId) return;
    const interval = setInterval(async () => {
      try {
        const batch = await getTask(tasks[0]?.task_id || '');
      } catch {
        // ignore
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [batchId]);

  const sourceFormat = convertFileIds.length === 1
    ? files.find((f) => f.id === convertFileIds[0])?.format || ''
    : '';

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-6">
      {/* 标题 */}
      <div className="flex items-center gap-3 mb-2">
        <BookOpen className="h-8 w-8 text-primary-600" />
        <div>
          <h1 className="text-2xl font-bold text-gray-900">EBook Converter</h1>
          <p className="text-sm text-gray-500">电子书格式转换工具</p>
        </div>
      </div>

      {/* 上传区域 */}
      <DropZone onFilesSelected={handleFilesSelected} uploading={uploading} />

      {/* 文件列表 */}
      <FileList
        files={files}
        loading={filesLoading}
        onRefresh={loadFiles}
        onConvert={handleConvert}
      />

      {/* 转换进度 */}
      {tasks.length > 0 && <ProgressBar tasks={tasks} />}

      {/* 转换对话框 */}
      {showConvert && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-lg m-4">
            <div className="p-5 border-b border-gray-100">
              <h2 className="text-lg font-semibold text-gray-800">
                转换设置 ({convertFileIds.length} 个文件)
              </h2>
            </div>

            <div className="p-5 space-y-4">
              <FormatSelector
                formats={formats}
                sourceFormat={sourceFormat}
                value={targetFormat}
                onChange={setTargetFormat}
              />

              {/* 元数据编辑按钮 */}
              {convertFileIds.length === 1 && (
                <button
                  className="btn-secondary w-full text-sm"
                  onClick={() => setEditingFileId(convertFileIds[0])}
                >
                  编辑元数据
                </button>
              )}

              <OptionPanel options={options} onChange={setOptions} />
            </div>

            <div className="p-5 border-t border-gray-100 flex justify-end gap-2">
              <button className="btn-secondary" onClick={() => setShowConvert(false)}>
                取消
              </button>
              <button
                className="btn-primary"
                onClick={handleStartConversion}
                disabled={!targetFormat}
              >
                开始转换
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 元数据编辑弹窗 */}
      <MetadataEditor
        fileId={editingFileId}
        onClose={() => {
          setEditingFileId(null);
          loadFiles();
        }}
      />
    </div>
  );
}
