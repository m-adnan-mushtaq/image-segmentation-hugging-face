import { LOADING_STEPS } from "../constants/backgrounds";
import type { ProcessStatus } from "../types";

interface PreviewPanelProps {
  status: ProcessStatus;
  loadingStep: number;
  resultUrl: string | null;
  error: string | null;
  onDownload: () => void;
  onReset: () => void;
}

function LoadingSkeleton({
  loadingStep,
  stepText,
}: {
  loadingStep: number;
  stepText: string;
}) {
  return (
    <div className="flex h-full flex-col">
      <div className="flex-1 space-y-4 rounded-2xl border border-violet-100 bg-white/70 p-6">
        <div className="h-4 w-1/3 animate-pulse rounded-full bg-violet-200" />
        <div className="aspect-video animate-pulse rounded-xl bg-violet-100" />
        <div className="space-y-2">
          <div className="h-3 w-full animate-pulse rounded-full bg-violet-100" />
          <div className="h-3 w-4/5 animate-pulse rounded-full bg-violet-100" />
          <div className="h-3 w-3/5 animate-pulse rounded-full bg-violet-100" />
        </div>
      </div>
      <p className="mt-6 text-center text-sm font-medium text-violet-600 animate-pulse">
        {stepText}
      </p>
      <div className="mt-3 flex justify-center gap-1.5">
        {LOADING_STEPS.map((_, index) => (
          <span
            key={index}
            className={`h-1.5 rounded-full transition-all ${
              index <= loadingStep
                ? "w-6 bg-violet-500"
                : "w-1.5 bg-violet-200"
            }`}
          />
        ))}
      </div>
    </div>
  );
}

function IdleState() {
  return (
    <div className="flex h-full flex-col items-center justify-center rounded-2xl border border-dashed border-violet-200 bg-white/50 px-8 py-16 text-center">
      <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-violet-100 text-violet-400">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-8 w-8"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={1.5}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909M3.75 21h16.5A2.25 2.25 0 0022.5 18.75V5.25A2.25 2.25 0 0020.25 3H3.75A2.25 2.25 0 001.5 5.25v13.5A2.25 2.25 0 003.75 21z"
          />
        </svg>
      </div>
      <p className="text-sm font-medium text-violet-700">
        Your result will appear here
      </p>
      <p className="mt-1 text-xs text-violet-400">
        Select a vehicle and background to get started
      </p>
    </div>
  );
}

export function PreviewPanel({
  status,
  loadingStep,
  resultUrl,
  error,
  onDownload,
  onReset,
}: PreviewPanelProps) {
  return (
    <section className="flex h-full min-h-[420px] flex-col">
      <div>
        <p className="text-xs font-semibold uppercase tracking-widest text-violet-400">
          Preview
        </p>
        <h2 className="mt-1 text-lg font-semibold text-violet-950">
          {status === "done" ? "Your new scene" : "Processing result"}
        </h2>
      </div>

      <div className="mt-4 flex flex-1 flex-col">
        {status === "processing" && (
          <LoadingSkeleton
            loadingStep={loadingStep}
            stepText={LOADING_STEPS[loadingStep]}
          />
        )}

        {status === "idle" && <IdleState />}

        {status === "error" && (
          <div className="flex h-full flex-col items-center justify-center rounded-2xl border border-red-200 bg-red-50/60 px-8 py-12 text-center">
            <p className="text-sm font-medium text-red-600">
              {error ?? "Something went wrong"}
            </p>
            <button
              type="button"
              onClick={onReset}
              className="mt-4 text-sm font-medium text-violet-600 underline-offset-2 hover:underline"
            >
              Start over
            </button>
          </div>
        )}

        {status === "done" && resultUrl && (
          <div className="flex h-full flex-col">
            <div className="flex-1 overflow-hidden rounded-2xl border border-violet-100 bg-white/70 p-3">
              <img
                src={resultUrl}
                alt="Processed vehicle"
                className="h-full w-full rounded-xl object-contain"
              />
            </div>
            <div className="mt-4 flex gap-3">
              <button
                type="button"
                onClick={onDownload}
                className="flex-1 rounded-xl bg-violet-600 py-3 text-sm font-semibold text-white transition-colors hover:bg-violet-700"
              >
                Download image
              </button>
              <button
                type="button"
                onClick={onReset}
                className="rounded-xl border border-violet-200 px-5 py-3 text-sm font-medium text-violet-600 transition-colors hover:bg-violet-50"
              >
                Reset
              </button>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
