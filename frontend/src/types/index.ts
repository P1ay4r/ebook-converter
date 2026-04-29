/** 文件信息 */
export interface FileItem {
  id: string;
  filename: string;
  format: string;
  size: number;
  status: string;
  created_at: string;
}

export interface FileListResponse {
  total: number;
  page: number;
  page_size: number;
  items: FileItem[];
}

/** 格式信息 */
export interface FormatsResponse {
  supported_formats: string[];
  conversion_matrix: Record<string, string[]>;
}

/** 转换参数 */
export interface ConversionOptions {
  margin_top?: number;
  margin_bottom?: number;
  margin_left?: number;
  margin_right?: number;
  base_font_size?: number;
  line_height?: number;
  embed_fonts?: boolean;
  compression_level?: number;
  remove_paragraph_spacing?: boolean;
  extra_css?: string;
}

export interface ConversionStartRequest {
  file_ids: string[];
  target_format: string;
  options?: ConversionOptions;
}

/** 任务信息 */
export interface TaskResponse {
  task_id: string;
  file_id: string;
  status: string;
  progress: number;
  progress_message?: string;
  source_format?: string;
  target_format?: string;
  created_at?: string;
  completed_at?: string;
  error_message?: string;
  output_file_id?: string;
}

export interface BatchStartResponse {
  batch_id: string;
  tasks: TaskResponse[];
}

export interface BatchStatusResponse {
  batch_id: string;
  total: number;
  completed: number;
  failed: number;
  processing: number;
  pending: number;
  tasks: TaskResponse[];
}

/** 元数据 */
export interface MetadataResponse {
  file_id: string;
  title?: string;
  author?: string;
  language?: string;
  isbn?: string;
  publisher?: string;
  pub_date?: string;
  tags?: string[];
  description?: string;
  cover_url?: string;
  updated_at: string;
}

export interface MetadataUpdate {
  title?: string;
  author?: string;
  language?: string;
  isbn?: string;
  publisher?: string;
  pub_date?: string;
  tags?: string[];
  description?: string;
}

/** WebSocket 进度消息 */
export interface WSProgressMessage {
  type: 'progress';
  task_id: string;
  progress: number;
  status: string;
}

/** 上传状态 */
export interface UploadState {
  uploading: boolean;
  progress: number;
  error?: string;
}
