export const SUPPORTED_LOCALES = ["zh-CN", "en"] as const;

export type Locale = (typeof SUPPORTED_LOCALES)[number];

export type TranslationValues = Record<string, string | number>;

export type Messages = Record<string, string>;
