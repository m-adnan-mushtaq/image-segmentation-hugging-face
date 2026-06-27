import { BackgroundPicker } from "./components/BackgroundPicker";
import { CarSelector } from "./components/CarSelector";
import { PreviewPanel } from "./components/PreviewPanel";
import { useCarReplace } from "./hooks/useCarReplace";

function App() {
  const {
    carPreview,
    selectedSampleId,
    background,
    status,
    loadingStep,
    resultUrl,
    error,
    canProcess,
    selectUploadedFile,
    selectSampleCar,
    selectBackground,
    processImage,
    reset,
  } = useCarReplace();

  const handleDownload = () => {
    if (!resultUrl) return;
    const link = document.createElement("a");
    link.href = resultUrl;
    link.download = "vehicle_processed.png";
    link.click();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-violet-50 via-purple-50 to-indigo-50">
      <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">
        <header className="mb-10 text-center">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-violet-400">
            Car Background Studio
          </p>
          <h1 className="mt-2 text-3xl font-bold tracking-tight text-violet-950 sm:text-4xl">
            Replace your vehicle background
          </h1>
          <p className="mx-auto mt-3 max-w-md text-sm text-violet-500">
            Upload a car photo or pick a sample, choose a scene, and get a
            polished result in seconds.
          </p>
        </header>

        <main className="grid gap-8 lg:grid-cols-2 lg:gap-12">
          <div className="space-y-8 rounded-2xl border border-violet-100 bg-white/60 p-6 backdrop-blur-sm sm:p-8">
            <CarSelector
              carPreview={carPreview}
              selectedSampleId={selectedSampleId}
              onSelectSample={selectSampleCar}
              onSelectFile={selectUploadedFile}
            />

            <div className="h-px bg-violet-100" />

            <BackgroundPicker
              selected={background}
              disabled={!carPreview}
              onSelect={selectBackground}
            />

            <button
              type="button"
              disabled={!canProcess}
              onClick={processImage}
              className="w-full rounded-xl bg-violet-600 py-3.5 text-sm font-semibold text-white transition-all hover:bg-violet-700 disabled:cursor-not-allowed disabled:opacity-40"
            >
              {status === "processing" ? "Processing…" : "Generate scene"}
            </button>
          </div>

          <div className="rounded-2xl border border-violet-100 bg-white/60 p-6 backdrop-blur-sm sm:p-8">
            <PreviewPanel
              status={status}
              loadingStep={loadingStep}
              resultUrl={resultUrl}
              error={error}
              onDownload={handleDownload}
              onReset={reset}
            />
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
