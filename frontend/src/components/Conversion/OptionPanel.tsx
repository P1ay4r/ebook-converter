import type { ConversionOptions } from '../../types';

interface OptionPanelProps {
  options: ConversionOptions;
  onChange: (options: ConversionOptions) => void;
}

export function OptionPanel({ options, onChange }: OptionPanelProps) {
  const update = (key: keyof ConversionOptions, value: any) => {
    onChange({ ...options, [key]: value });
  };

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold text-gray-700">高级选项</h3>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="label">基础字号 (pt)</label>
          <input
            type="number"
            className="input"
            min={8}
            max={72}
            value={options.base_font_size ?? ''}
            onChange={(e) => update('base_font_size', e.target.value ? Number(e.target.value) : undefined)}
            placeholder="默认"
          />
        </div>

        <div>
          <label className="label">行距</label>
          <input
            type="number"
            className="input"
            min={1}
            max={3}
            step={0.1}
            value={options.line_height ?? ''}
            onChange={(e) => update('line_height', e.target.value ? Number(e.target.value) : undefined)}
            placeholder="默认"
          />
        </div>

        <div>
          <label className="label">上边距 (mm)</label>
          <input
            type="number"
            className="input"
            min={0}
            value={options.margin_top ?? ''}
            onChange={(e) => update('margin_top', e.target.value ? Number(e.target.value) : undefined)}
          />
        </div>

        <div>
          <label className="label">下边距 (mm)</label>
          <input
            type="number"
            className="input"
            min={0}
            value={options.margin_bottom ?? ''}
            onChange={(e) => update('margin_bottom', e.target.value ? Number(e.target.value) : undefined)}
          />
        </div>

        <div>
          <label className="label">左边距 (mm)</label>
          <input
            type="number"
            className="input"
            min={0}
            value={options.margin_left ?? ''}
            onChange={(e) => update('margin_left', e.target.value ? Number(e.target.value) : undefined)}
          />
        </div>

        <div>
          <label className="label">右边距 (mm)</label>
          <input
            type="number"
            className="input"
            min={0}
            value={options.margin_right ?? ''}
            onChange={(e) => update('margin_right', e.target.value ? Number(e.target.value) : undefined)}
          />
        </div>

        <div>
          <label className="label">压缩级别 (0-9)</label>
          <input
            type="number"
            className="input"
            min={0}
            max={9}
            value={options.compression_level ?? ''}
            onChange={(e) => update('compression_level', e.target.value ? Number(e.target.value) : undefined)}
          />
        </div>

        <div className="flex items-end pb-2">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              className="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
              checked={options.embed_fonts ?? false}
              onChange={(e) => update('embed_fonts', e.target.checked)}
            />
            <span className="text-sm text-gray-700">嵌入字体</span>
          </label>
        </div>
      </div>
    </div>
  );
}
