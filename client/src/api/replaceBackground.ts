import axios from "axios";

import type { BackgroundId } from "../types";
import { apiClient } from "./axiosInstance";

function getErrorMessage(error: unknown): string {
  if (!axios.isAxiosError(error)) {
    return error instanceof Error ? error.message : "Failed to process image";
  }

  const data = error.response?.data;

  if (data instanceof Blob) {
    return "Image processing failed";
  }

  if (typeof data === "object" && data !== null && "detail" in data) {
    const detail = (data as { detail: unknown }).detail;
    return typeof detail === "string" ? detail : "Image processing failed";
  }

  return error.message || "Failed to process image";
}

export async function replaceBackground(
  image: File,
  background: BackgroundId,
): Promise<Blob> {
  const formData = new FormData();
  formData.append("image", image);
  formData.append("background", background);

  try {
    const response = await apiClient.post<Blob>("/replace-bg", formData, {
      responseType: "blob",
    });

    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error), { cause: error });
  }
}
