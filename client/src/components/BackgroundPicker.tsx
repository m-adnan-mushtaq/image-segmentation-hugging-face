import { BACKGROUNDS } from "../constants/backgrounds";
import type { BackgroundId } from "../types";

interface BackgroundPickerProps {
  selected: BackgroundId | null;
  disabled: boolean;
  onSelect: (id: BackgroundId) => void;
}

export function BackgroundPicker({
  selected,
  disabled,
  onSelect,
}: BackgroundPickerProps) {
  return (
    <section className="space-y-4">
      <div>
        <p className="text-xs font-semibold uppercase tracking-widest text-violet-400">
          Step 2
        </p>
        <h2 className="mt-1 text-lg font-semibold text-violet-950">
          Pick a background
        </h2>
      </div>

      <div className="grid grid-cols-3 gap-3">
        {BACKGROUNDS.map((bg) => {
          const isSelected = selected === bg.id;
          return (
            <button
              key={bg.id}
              type="button"
              disabled={disabled}
              onClick={() => onSelect(bg.id)}
              className={`overflow-hidden rounded-xl border-2 transition-all disabled:cursor-not-allowed disabled:opacity-40 ${
                isSelected
                  ? "border-violet-500 ring-2 ring-violet-200"
                  : "border-violet-100 hover:border-violet-300"
              }`}
            >
              <img
                src={bg.image}
                alt={bg.label}
                className="aspect-video w-full object-cover"
              />
              <span
                className={`block py-2 text-xs font-medium ${
                  isSelected ? "text-violet-700" : "text-violet-500"
                }`}
              >
                {bg.label}
              </span>
            </button>
          );
        })}
      </div>
    </section>
  );
}
