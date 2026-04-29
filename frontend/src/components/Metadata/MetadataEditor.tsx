import { useState, useEffect } from 'react';
import { Save } from 'lucide-react';
import type { MetadataResponse, MetadataUpdate } from '../../types';
import { getMetadata, updateMetadata } from '../../api/metadata';

interface MetadataEditorProps {
  fileId: string | null;
  onClose: () => void;
}

export function MetadataEditor({ fileId, onClose }: MetadataEditorProps) {
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState<MetadataUpdate>({});
  const [error, setError] = useState('');

  useEffect(() => {
    if (!fileId) return;
    setLoading(true);
    getMetadata(fileId)
      .then((meta) => {
        setForm({
          title: meta.title || '',
          author: meta.author || '',
          language: meta.language || '',
          isbn: meta.isbn || '',
          publisher: meta.publisher || '',
          pub_date: meta.pub_date || '',
          tags: meta.tags || [],
          description: meta.description || '',
        });
      })
      .catch(() => setError('加载元数据失败'))
      .finally(() => setLoading(false));
  }, [fileId]);

  const handleSave = async () => {
    if (!fileId) return;
    setSaving(true);
    setError('');
    try {
      await updateMetadata(fileId, form);
      onClose();
    } catch (e: any) {
      setError(e.message || '保存失败');
    }
    setSaving(false);
  };

  const handleTagInput = (value: string) => {
    const tags = value.split(/[,，、]/).map((t) => t.trim()).filter(Boolean);
    setForm({ ...form, tags });
  };

  if (!fileId) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-white rounded-xl shadow-xl w-full max-w-lg max-h-[80vh] overflow-y-auto m-4" onClick={(e) => e.stopPropagation()}>
        <div className="p-5 border-b border-gray-100">
          <h2 className="text-lg font-semibold text-gray-800">编辑元数据</h2>
        </div>

        {loading ? (
          <div className="p-8 text-center text-gray-500">加载中...</div>
        ) : (
          <div className="p-5 space-y-4">
            {error && (
              <div className="bg-red-50 text-red-600 text-sm p-3 rounded-lg">{error}</div>
            )}

            <div>
              <label className="label">书名 *</label>
              <input
                className="input"
                value={form.title || ''}
                onChange={(e) => setForm({ ...form, title: e.target.value })}
              />
            </div>

            <div>
              <label className="label">作者</label>
              <input
                className="input"
                value={form.author || ''}
                onChange={(e) => setForm({ ...form, author: e.target.value })}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="label">语言</label>
                <input
                  className="input"
                  placeholder="zh / en"
                  value={form.language || ''}
                  onChange={(e) => setForm({ ...form, language: e.target.value })}
                />
              </div>
              <div>
                <label className="label">ISBN</label>
                <input
                  className="input"
                  value={form.isbn || ''}
                  onChange={(e) => setForm({ ...form, isbn: e.target.value })}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="label">出版社</label>
                <input
                  className="input"
                  value={form.publisher || ''}
                  onChange={(e) => setForm({ ...form, publisher: e.target.value })}
                />
              </div>
              <div>
                <label className="label">出版日期</label>
                <input
                  className="input"
                  placeholder="YYYY-MM-DD"
                  value={form.pub_date || ''}
                  onChange={(e) => setForm({ ...form, pub_date: e.target.value })}
                />
              </div>
            </div>

            <div>
              <label className="label">标签（逗号分隔）</label>
              <input
                className="input"
                value={(form.tags || []).join(', ')}
                onChange={(e) => handleTagInput(e.target.value)}
              />
            </div>

            <div>
              <label className="label">简介</label>
              <textarea
                className="input min-h-[80px]"
                value={form.description || ''}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
              />
            </div>
          </div>
        )}

        <div className="p-5 border-t border-gray-100 flex justify-end gap-2">
          <button className="btn-secondary" onClick={onClose}>取消</button>
          <button className="btn-primary" onClick={handleSave} disabled={saving || loading}>
            <Save className="h-4 w-4 mr-1" />
            {saving ? '保存中...' : '保存'}
          </button>
        </div>
      </div>
    </div>
  );
}
