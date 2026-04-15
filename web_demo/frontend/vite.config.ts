import { defineConfig, loadEnv } from "vite";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, ".", "");
  const backendUrl = env.VITE_BACKEND_URL || "http://localhost:8000";
  const appVersion = env.VITE_APP_VERSION || "0.0.0";

  return {
    base: "/dap3d/",
    define: {
      __APP_VERSION__: JSON.stringify(appVersion),
    },
    server: {
      port: 5173,
      proxy: {
        "/api": backendUrl,
        "/artifacts": backendUrl,
      },
    },
    build: {
      chunkSizeWarningLimit: 1500,
      rollupOptions: {
        onwarn(warning, warn) {
          if (warning.code === "MODULE_LEVEL_DIRECTIVE") return;
          if (warning.message?.includes('"use client"')) return;
          warn(warning);
        },
        output: {
          manualChunks: {
            three: ["three"],
            r3f: ["@react-three/fiber", "@react-three/drei"],
            query: ["@tanstack/react-query"],
            react: ["react", "react-dom"],
          },
        },
      },
    },
  };
});
