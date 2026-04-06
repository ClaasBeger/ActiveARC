import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Relative asset paths work with st.components.declare_component(build_dir).
export default defineConfig({
  plugins: [react()],
  base: "./",
  build: {
    outDir: "../build",
    emptyOutDir: true,
  },
});
