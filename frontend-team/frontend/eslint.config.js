import js from "@eslint/js";
import globals from "globals";
import pluginReact from "eslint-plugin-react";
import { defineConfig } from "eslint/config";

export default defineConfig([
  {
    files: ["**/*.{js,mjs,cjs,jsx}"],
    languageOptions: {
      globals: globals.browser,
      parserOptions: {
        ecmaFeatures: {
          jsx: true
        }
      }
    }
  },

  
  pluginReact.configs.flat.recommended,

 
  {
    rules: {
      "react/react-in-jsx-scope": "off",
      "react/no-unescaped-entities": "warn",
      "no-unused-vars": "warn",
      "no-console": "warn",
      "no-constant-condition": "warn"
    },
    settings: {
      react: {
        version: "detect"
      }
    }
  }
]);