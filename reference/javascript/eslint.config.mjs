// Flat config for ESLint v9+
import tseslint from 'typescript-eslint';
import eslintJs from '@eslint/js';

export default tseslint.config(
  eslintJs.configs.recommended,
  ...tseslint.configs.recommended,
  {
    ignores: ['node_modules', 'public', 'remotes', 'dist'],
  },
  {
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
    },
    rules: {
      '@typescript-eslint/no-explicit-any': 'off',
      '@typescript-eslint/no-require-imports': 'off',
    },
  }
);

