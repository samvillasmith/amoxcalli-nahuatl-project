import { defineConfig } from "@neon/config/v1";
import { fileURLToPath } from "node:url";

export default defineConfig({
  functions: {
    lexiconsearch: {
      name: "Amoxcalli public lexicon search",
      source: fileURLToPath(new URL("./functions/search/index.mjs", import.meta.url)),
      env: { AMOXCALLI_ORIGIN_SECRET: process.env.AMOXCALLI_ORIGIN_SECRET! },
    },
  },
});
