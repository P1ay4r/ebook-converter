import { CheckCircle, XCircle, Loader2 } from 'lucide-react';
import type { TaskResponse } from '../../types';

interface ProgressBarProps {
  tasks: TaskResponse[];
}

const STATUS_ICONS: Record<string, React.ReactNode> = {
  completed: <CheckCircle className="h-5 w-5 text-green-500" />,
  failed: <XCircle className="h-5 w-5 text-red-500" />,
  processing: <Loader2 className="h-5 w-5 text-primary-500 animate-spin" />,
  pending: <Loader2 className="h-5 w-5 text-gray-300 animate-spin" />,
  cancelled: <XCircle className="h-5 w-5 text-gray-400" />,
};

const STATUS_LABELS: Record<string, string> = {
  pending: '排队中',
  processing: '转换中',
  completed: '已完成',
  failed: '失败',
  cancelled: '已取消',
};

export function ProgressBar({ tasks }: ProgressBarProps) {
  if (tasks.length === 0) return null;

  const total = tasks.length;
  const completed = tasks.filter((t) => t.status === 'completed').length;
  const failed = tasks.filter((t) => t.status === 'failed').length;
  const active = tasks.filter((t) => t.status === 'processing').length;

  return (
    <div className="card p-4 space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-gray-800">转换进度</h3>
        <span className="text-sm text-gray-500">
          {completed + failed}/{total} · {active > 0 && `转换中 ${active} 项`}
        </span>
      </div>

      {/* 总体进度条 */}
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className="bg-primary-600 h-2 rounded-full transition-all duration-500"
          style={{ width: `${total > 0 ? ((completed + failed) / total) * 100 : 0}%` }}
        />
      </div>

      {/* 每个任务的进度 */}
      <div className="space-y-2 max-h-60 overflow-y-auto">
        {tasks.map((task) => (
          <div key={task.task_id} className="flex items-center gap-2 text-sm">
            {STATUS_ICONS[task.status] || <Loader2 className="h-4 w-4 text-gray-300" />}
            <span className="flex-1 truncate text-gray-700">
              {task.source_format?.toUpperCase()} → {task.target_format?.toUpperCase()}
            </span>
            <span className="text-gray-400 w-16 text-right">
              {task.status === 'processing' ? `${task.progress}%` : STATUS_LABELS[task.status]}
            </span>
            {task.status === 'completed' && task.output_file_id && (
              <a
                href={`/api/v1/files/${task.output_file_id}/download`}
                className="text-primary-600 hover:text-primary-700 text-xs font-medium"
              >
                下载
              </a>
            )}
            {task.status === 'failed' && task.error_message && (
              <span className="text-xs text-red-500 truncate max-w-[200px]" title={task.error_message}>
                {task.error_message}
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
