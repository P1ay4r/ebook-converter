import type { FormatsResponse } from '../../types';

interface FormatSelectorProps {
  formats: FormatsResponse | null;
  sourceFormat: string;
  value: string;
  onChange: (format: string) => void;
}

const FORMAT_LABELS: Record<string, string> = {
  epub: 'EPUB',
  mobi: 'MOBI (Kindle)',
  azw3: 'AZW3 (Kindle)',
  pdf: 'PDF',
  txt: 'TXT',
  docx: 'DOCX (Word)',
  html: 'HTML',
  fb2: 'FB2',
  cbz: 'CBZ (漫画)',
  cbr: 'CBR (漫画)',
};

export function FormatSelector({ formats, sourceFormat, value, onChange }: FormatSelectorProps) {
  const targets = formats?.conversion_matrix[sourceFormat] || [];

  if (!sourceFormat) {
    return (
      <div className="text-sm text-gray-500 italic">请先选择源文件</div>
    );
  }

  if (targets.length === 0) {
    return (
      <div className="text-sm text-red-500">不支持此格式的转换</div>
    );
  }

  return (
    <div>
      <label className="label">目标格式</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="input"
      >
        <option value="">请选择...</option>
        {targets.map((fmt) => (
          <option key={fmt} value={fmt}>
            {FORMAT_LABELS[fmt] || fmt.toUpperCase()}
          </option>
        ))}
      </select>
    </div>
  );
}
