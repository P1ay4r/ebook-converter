import { useState, useRef, type DragEvent } from 'react';
import { Upload } from 'lucide-react';

interface DropZoneProps {
  onFilesSelected: (files: File[]) => void;
  uploading: boolean;
}

const ALLOWED_EXTENSIONS = [
  '.epub', '.mobi', '.azw3', '.pdf', '.txt',
  '.docx', '.html', '.fb2', '.cbz', '.cbr',
];

export function DropZone({ onFilesSelected, uploading }: DropZoneProps) {
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragOver(false);
    const files = Array.from(e.dataTransfer.files).filter((f) =>
      ALLOWED_EXTENSIONS.some((ext) => f.name.toLowerCase().endsWith(ext))
    );
    if (files.length > 0) onFilesSelected(files);
  };

  const handleClick = () => {
    inputRef.current?.click();
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length > 0) onFilesSelected(files);
    e.target.value = '';
  };

  return (
    <div
      className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors
        ${dragOver
          ? 'border-primary-500 bg-primary-50'
          : 'border-gray-300 hover:border-gray-400 bg-white'
        }
        ${uploading ? 'opacity-50 pointer-events-none' : ''}
      `}
      onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
      onDragLeave={() => setDragOver(false)}
      onDrop={handleDrop}
      onClick={handleClick}
    >
      <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
      <p className="text-lg font-medium text-gray-700 mb-1">
        {uploading ? '上传中...' : '拖拽电子书文件到此处'}
      </p>
      <p className="text-sm text-gray-500">
        或点击选择文件 · 支持 EPUB / MOBI / AZW3 / PDF / TXT / DOCX / HTML / FB2 / CBZ / CBR
      </p>
      <p className="text-xs text-gray-400 mt-2">单文件最大 200MB</p>
      <input
        ref={inputRef}
        type="file"
        className="hidden"
        multiple
        accept={ALLOWED_EXTENSIONS.join(',')}
        onChange={handleFileInput}
      />
    </div>
  );
}
