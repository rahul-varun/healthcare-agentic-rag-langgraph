import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  // Override default ignores of eslint-config-next.
  globalIgnores([
    // Default ignores of eslint-config-next:
    ".next/**",
    "out/**",
    "build/**",
    "next-env.d.ts",
    // This project lives on an exFAT volume, which makes macOS write a
    // "._name" AppleDouble sidecar next to every file — ESLint's glob matches
    // "._page.tsx" as a real .tsx file otherwise.
    "**/._*",
  ]),
]);

export default eslintConfig;
