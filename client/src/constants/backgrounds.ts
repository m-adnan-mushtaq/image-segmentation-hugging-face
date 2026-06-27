import type { BackgroundOption, SampleCar } from "../types";

export const BACKGROUNDS: BackgroundOption[] = [
  { id: "studio", label: "Studio", image: "/studio.jpg" },
  { id: "road", label: "Road", image: "/road.jpg" },
  { id: "showroom", label: "Showroom", image: "/showroom.jpg" },
];

export const SAMPLE_CARS: SampleCar[] = [
  {
    id: "sample-1",
    label: "Sample 1",
    image: "/car-input-1.jpg",
    filename: "car-input-1.jpg",
  },
  {
    id: "sample-2",
    label: "Sample 2",
    image: "/car-input-2.jpeg",
    filename: "car-input-2.jpeg",
  },
];

export const LOADING_STEPS = [
  "Just a moment…",
  "Reading your vehicle image…",
  "Removing the background…",
  "Placing your car in the scene…",
  "Adding final touches…",
];
