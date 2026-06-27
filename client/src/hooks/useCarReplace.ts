import { useCallback, useEffect, useRef, useState } from "react";

import { replaceBackground } from "../api/replaceBackground";
import { LOADING_STEPS } from "../constants/backgrounds";
import type { BackgroundId, ProcessStatus } from "../types";

async function urlToFile(url: string, filename: string): Promise<File> {
  const response = await fetch(url);
  const blob = await response.blob();
  return new File([blob], filename, { type: blob.type || "image/jpeg" });
}

export function useCarReplace() {
  const [carFile, setCarFile] = useState<File | null>(null);
  const [carPreview, setCarPreview] = useState<string | null>(null);
  const [selectedSampleId, setSelectedSampleId] = useState<string | null>(null);
  const [background, setBackground] = useState<BackgroundId | null>(null);
  const [status, setStatus] = useState<ProcessStatus>("idle");
  const [loadingStep, setLoadingStep] = useState(0);
  const [resultUrl, setResultUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const previewRef = useRef<string | null>(null);
  const resultRef = useRef<string | null>(null);

  const revokePreview = useCallback(() => {
    if (previewRef.current) {
      URL.revokeObjectURL(previewRef.current);
      previewRef.current = null;
    }
  }, []);

  const revokeResult = useCallback(() => {
    if (resultRef.current) {
      URL.revokeObjectURL(resultRef.current);
      resultRef.current = null;
    }
  }, []);

  const setPreview = useCallback(
    (file: File) => {
      revokePreview();
      const url = URL.createObjectURL(file);
      previewRef.current = url;
      setCarPreview(url);
      setCarFile(file);
    },
    [revokePreview],
  );

  const selectUploadedFile = useCallback(
    (file: File) => {
      setSelectedSampleId(null);
      setBackground(null);
      revokeResult();
      setResultUrl(null);
      setStatus("idle");
      setError(null);
      setPreview(file);
    },
    [revokeResult, setPreview],
  );

  const selectSampleCar = useCallback(
    async (url: string, filename: string, sampleId: string) => {
      setSelectedSampleId(sampleId);
      setBackground(null);
      revokeResult();
      setResultUrl(null);
      setStatus("idle");
      setError(null);
      const file = await urlToFile(url, filename);
      setPreview(file);
    },
    [revokeResult, setPreview],
  );

  const selectBackground = useCallback((id: BackgroundId) => {
    setBackground(id);
    setError(null);
  }, []);

  const reset = useCallback(() => {
    revokePreview();
    revokeResult();
    setCarFile(null);
    setCarPreview(null);
    setSelectedSampleId(null);
    setBackground(null);
    setStatus("idle");
    setLoadingStep(0);
    setResultUrl(null);
    setError(null);
  }, [revokePreview, revokeResult]);

  const processImage = useCallback(async () => {
    if (!carFile || !background) return;

    revokeResult();
    setResultUrl(null);
    setStatus("processing");
    setLoadingStep(0);
    setError(null);

    try {
      const blob = await replaceBackground(carFile, background);
      const url = URL.createObjectURL(blob);
      resultRef.current = url;
      setResultUrl(url);
      setStatus("done");
    } catch (err) {
      setStatus("error");
      setError(err instanceof Error ? err.message : "Something went wrong");
    }
  }, [background, carFile, revokeResult]);

  useEffect(() => {
    if (status !== "processing") return;

    const interval = setInterval(() => {
      setLoadingStep((prev) =>
        prev < LOADING_STEPS.length - 1 ? prev + 1 : prev,
      );
    }, 2200);

    return () => clearInterval(interval);
  }, [status]);

  useEffect(() => {
    return () => {
      revokePreview();
      revokeResult();
    };
  }, [revokePreview, revokeResult]);

  const canProcess = Boolean(carFile && background && status !== "processing");

  return {
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
  };
}
