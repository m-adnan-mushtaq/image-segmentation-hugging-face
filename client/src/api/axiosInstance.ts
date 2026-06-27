import axios from "axios";

const baseURL = import.meta.env.API_URL;

if (!baseURL) {
  throw new Error("API_URL is not defined in client/.env");
}

export const apiClient = axios.create({
  baseURL,
});
