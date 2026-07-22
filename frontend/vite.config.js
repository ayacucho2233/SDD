import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    // Necesario en WSL2 cuando el proyecto vive en un filesystem de Windows
    // montado (/mnt/c/...): inotify no recibe los eventos de cambio de
    // archivo ahí, así que el watcher normal de Vite no dispara HMR.
    watch: {
      usePolling: true,
      interval: 300,
    },
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: "./tests/setup.js",
  },
});
