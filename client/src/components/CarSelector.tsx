import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";

import { SAMPLE_CARS } from "../constants/backgrounds";
import {
  MAX_UPLOAD_SIZE_BYTES,
  MAX_UPLOAD_SIZE_MB,
} from "../constants/upload";

interface CarSelectorProps {
  carPreview: string | null;
  selectedSampleId: string | null;
  onSelectSample: (url: string, filename: string, sampleId: string) => void;
  onSelectFile: (file: File) => void;
}

export function CarSelector({
  carPreview,
  selectedSampleId,
  onSelectSample,
  onSelectFile,
}: CarSelectorProps) {
  const [uploadError, setUploadError] = useState<string | null>(null);

  const onDrop = useCallback(
    (files: File[]) => {
      const file = files[0];
      if (file) {
        setUploadError(null);
        onSelectFile(file);
      }
    },
    [onSelectFile],
  );

  const onDropRejected = useCallback(() => {
    setUploadError(`File must be ${MAX_UPLOAD_SIZE_MB} MB or smaller`);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    onDropRejected,
    accept: { "image/*": [".jpg", ".jpeg", ".png", ".webp"] },
    maxFiles: 1,
    maxSize: MAX_UPLOAD_SIZE_BYTES,
    multiple: false,
  });

  return (
    <section className="space-y-4">
      <div>
        <p className="text-xs font-semibold uppercase tracking-widest text-violet-400">
          Step 1
        </p>
        <h2 className="mt-1 text-lg font-semibold text-violet-950">
          Choose your vehicle
        </h2>
      </div>

      <div className="grid grid-cols-2 gap-3">
        {SAMPLE_CARS.map((car) => {
          const isSelected = selectedSampleId === car.id;
          return (
            <button
              key={car.id}
              type="button"
              onClick={() => onSelectSample(car.image, car.filename, car.id)}
              className={`group overflow-hidden rounded-xl border-2 transition-all ${
                isSelected
                  ? "border-violet-500 ring-2 ring-violet-200"
                  : "border-violet-100 hover:border-violet-300"
              }`}
            >
              <img
                src={car.image}
                alt={car.label}
                className="aspect-[4/3] w-full object-cover"
              />
              <span
                className={`block py-2 text-sm font-medium ${
                  isSelected ? "text-violet-700" : "text-violet-500"
                }`}
              >
                {car.label}
              </span>
            </button>
          );
        })}
      </div>

      <div
        {...getRootProps()}
        className={`cursor-pointer rounded-xl border-2 border-dashed px-4 py-8 text-center transition-colors ${
          uploadError
            ? "border-red-300 bg-red-50/60"
            : isDragActive
              ? "border-violet-500 bg-violet-100/60"
              : "border-violet-200 bg-white/60 hover:border-violet-400 hover:bg-violet-50"
        }`}
      >
        <input {...getInputProps()} />
        {carPreview && !selectedSampleId ? (
          <img
            src={carPreview}
            alt="Uploaded vehicle"
            className="mx-auto mb-3 max-h-32 rounded-lg object-contain"
          />
        ) : (
          <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-violet-100 text-violet-500">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={1.5}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"
              />
            </svg>
          </div>
        )}
        <p className="text-sm font-medium text-violet-800">
          {isDragActive ? "Drop your image here" : "Drag & drop or click to upload"}
        </p>
        <p className="mt-1 text-xs text-violet-400">
          JPG, PNG or WEBP · max {MAX_UPLOAD_SIZE_MB} MB
        </p>
        {uploadError && (
          <p className="mt-2 text-xs font-medium text-red-500">{uploadError}</p>
        )}
      </div>
    </section>
  );
}
