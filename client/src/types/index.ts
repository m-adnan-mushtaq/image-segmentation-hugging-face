export type ProcessStatus = "idle" | "processing" | "done" | "error";

export type BackgroundId = "studio" | "road" | "showroom";

export interface BackgroundOption {
  id: BackgroundId;
  label: string;
  image: string;
}

export interface SampleCar {
  id: string;
  label: string;
  image: string;
  filename: string;
}
