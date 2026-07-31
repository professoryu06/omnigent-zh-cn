import {
  createContext,
  createElement,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { en } from "./locales/en";
import { zhCN } from "./locales/zh-CN";
import { SUPPORTED_LOCALES, type Locale, type TranslationValues } from "./types";

export const DEFAULT_LOCALE: Locale = "zh-CN";
export const TRANSLATION_STORAGE_KEY = "omnigent:locale";

const messages: Record<Locale, Record<string, string>> = {
  "zh-CN": zhCN,
  en,
};

type TranslationContextValue = {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  t: (key: string, values?: TranslationValues) => string;
};

const TranslationContext = createContext<TranslationContextValue | null>(null);
let pinnedDefaultLocale: Locale | null = null;

function isLocale(value: string | null): value is Locale {
  return value !== null && (SUPPORTED_LOCALES as readonly string[]).includes(value);
}

function applyDocumentLanguage(locale: Locale): void {
  if (typeof document !== "undefined") {
    document.documentElement.lang = locale;
  }
}

export function getLocale(): Locale {
  if (typeof window === "undefined") return DEFAULT_LOCALE;

  const storedLocale = window.localStorage.getItem(TRANSLATION_STORAGE_KEY);
  return isLocale(storedLocale) ? storedLocale : (pinnedDefaultLocale ?? DEFAULT_LOCALE);
}

/** Test-only override for legacy component suites that assert English copy. */
export function __pinDefaultLocale(locale: Locale | null): void {
  pinnedDefaultLocale = locale;
}

export function setLocale(locale: Locale): void {
  if (typeof window !== "undefined") {
    window.localStorage.setItem(TRANSLATION_STORAGE_KEY, locale);
  }
  applyDocumentLanguage(locale);
}

export function translate(
  key: string,
  values: TranslationValues = {},
  locale: Locale = getLocale(),
): string {
  const template = messages[locale][key] ?? messages.en[key] ?? key;

  return template.replace(/{{(\w+)}}/g, (match, name: string) => {
    const value = values[name];
    return value === undefined ? match : String(value);
  });
}

export function I18nProvider({ children }: { children: ReactNode }) {
  const [locale, setActiveLocale] = useState<Locale>(getLocale);

  useEffect(() => {
    applyDocumentLanguage(locale);
  }, [locale]);

  const value = useMemo<TranslationContextValue>(
    () => ({
      locale,
      setLocale: (nextLocale) => {
        setLocale(nextLocale);
        setActiveLocale(nextLocale);
      },
      t: (key, values) => translate(key, values, locale),
    }),
    [locale],
  );

  return createElement(TranslationContext.Provider, { value }, children);
}

export function useTranslation(): TranslationContextValue {
  const context = useContext(TranslationContext);
  if (context === null) {
    return {
      locale: getLocale(),
      setLocale,
      t: (key, values) => translate(key, values),
    };
  }
  return context;
}
