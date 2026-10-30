/* eslint-disable react-refresh/only-export-components */

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import {
  BACKEND_STRINGS_TRANSLATIONS_SOURCE,
  LITERAL_FALLBACK_TRANSLATIONS,
  LITERAL_TRANSLATIONS,
  MESSAGES,
} from '../i18n/messages';

const SUPPORTED_LANGUAGES = ['es-LATAM', 'en', 'pt'];
const DEFAULT_LANGUAGE = 'es-LATAM';
const LANGUAGE_STORAGE_KEY = 'isosmart_language';

const getStoredLanguage = () => {
  if (typeof window === 'undefined') return DEFAULT_LANGUAGE;
  const stored = window.localStorage.getItem(LANGUAGE_STORAGE_KEY);
  return SUPPORTED_LANGUAGES.includes(stored) ? stored : DEFAULT_LANGUAGE;
};

const translateLiteralFallback = (literalKey, language) => {
  const dictionary = LITERAL_FALLBACK_TRANSLATIONS[language];
  if (!dictionary) return literalKey;

  if (dictionary[literalKey] !== undefined) {
    return dictionary[literalKey];
  }

  const entries = Object.entries(dictionary).sort((a, b) => b[0].length - a[0].length);
  let translated = literalKey;

  for (const [source, target] of entries) {
    if (!source) continue;
    translated = translated.split(source).join(target);
  }

  return translated;
};

const normalizeBackendTranslationKey = (value) => {
  if (typeof value !== 'string') return value;
  return value
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/\s+/g, ' ')
    .trim();
};

// Canonical backend strings translations for dynamic content from API.
// Variants without accents/case are generated automatically below.
const BACKEND_STRINGS_TRANSLATIONS = Object.fromEntries(
  Object.entries(BACKEND_STRINGS_TRANSLATIONS_SOURCE).map(([languageKey, dictionary]) => {
    const expandedEntries = Object.entries(dictionary).flatMap(([source, target]) => {
      const normalized = normalizeBackendTranslationKey(source);
      return [
        [source, target],
        [normalized, target],
        [normalized.toLowerCase(), target],
      ];
    });

    return [languageKey, Object.fromEntries(expandedEntries)];
  })
);

const I18nContext = createContext(null);

const getValue = (obj, path) => {
  return path.split('.').reduce((acc, key) => (acc && acc[key] !== undefined ? acc[key] : undefined), obj);
};

const interpolate = (message, values) => {
  if (typeof message !== 'string' || !values || typeof values !== 'object' || Array.isArray(values)) {
    return message;
  }

  return message.replace(/\{(\w+)\}/g, (match, key) => (
    values[key] === undefined || values[key] === null ? match : String(values[key])
  ));
};

const buildBackendLookupCandidates = (value) => {
  const raw = typeof value === 'string' ? value : '';
  const trimmed = raw.trim();
  const withoutBullet = trimmed.replace(/^[-*•]\s*/, '');
  const withoutTrailingPunctuation = withoutBullet.replace(/[.,;:!?]+$/g, '').trim();

  return [
    trimmed,
    withoutBullet,
    withoutTrailingPunctuation,
    normalizeBackendTranslationKey(trimmed),
    normalizeBackendTranslationKey(withoutBullet),
    normalizeBackendTranslationKey(withoutTrailingPunctuation),
    normalizeBackendTranslationKey(trimmed).toLowerCase(),
    normalizeBackendTranslationKey(withoutBullet).toLowerCase(),
    normalizeBackendTranslationKey(withoutTrailingPunctuation).toLowerCase(),
  ].filter(Boolean);
};

const translateByBackendDictionaryFragments = (value, language) => {
  const dictionary = BACKEND_STRINGS_TRANSLATIONS[language];
  if (!dictionary) return value;

  const normalizedEntries = Object.entries(dictionary)
    .flatMap(([source, target]) => {
      const normalized = normalizeBackendTranslationKey(source);
      return [[normalized, target], [normalized.toLowerCase(), target]];
    })
    .sort((a, b) => b[0].length - a[0].length);

  let translated = normalizeBackendTranslationKey(value);

  for (const [source, target] of normalizedEntries) {
    if (!source) continue;
    translated = translated.split(source).join(target);
  }

  return translated;
};

export const I18nProvider = ({ children }) => {
  const [language, setLanguageState] = useState(getStoredLanguage);

  const setLanguage = useCallback((nextLanguage) => {
    const normalized = SUPPORTED_LANGUAGES.includes(nextLanguage) ? nextLanguage : DEFAULT_LANGUAGE;
    if (typeof window !== 'undefined') {
      window.localStorage.setItem(LANGUAGE_STORAGE_KEY, normalized);
    }
    setLanguageState(normalized);
  }, []);

  useEffect(() => {
    document.documentElement.lang = language;
  }, [language]);

  const t = useCallback(
    (key, fallbackOrValues = key, maybeValues) => {
      const hasFallbackString = typeof fallbackOrValues === 'string';
      const fallback = hasFallbackString ? fallbackOrValues : key;
      const values = hasFallbackString ? maybeValues : fallbackOrValues;

      if (typeof key === 'string' && key.startsWith('literals.')) {
        const literalKey = key.slice('literals.'.length);
        const translatedLiteral = LITERAL_TRANSLATIONS[language]?.[literalKey];
        if (translatedLiteral !== undefined) return interpolate(translatedLiteral, values);
        if (language === DEFAULT_LANGUAGE) return interpolate(literalKey, values);
        return interpolate(translateLiteralFallback(literalKey, language), values);
      }

      const primary = getValue(MESSAGES[language], key);
      if (primary !== undefined) return interpolate(primary, values);
      const defaultValue = getValue(MESSAGES[DEFAULT_LANGUAGE], key);
      return interpolate(defaultValue !== undefined ? defaultValue : fallback, values);
    },
    [language]
  );

  // Translate dynamic strings from backend API responses
  const translateBackendString = useCallback(
    (backendString) => {
      if (!backendString || typeof backendString !== 'string') return backendString;
      const leadingPrefixMatch = backendString.match(/^\s*([-*•]\s*)/);
      const leadingPrefix = leadingPrefixMatch ? leadingPrefixMatch[0] : '';
      const stringBody = leadingPrefix ? backendString.slice(leadingPrefix.length) : backendString;

      const candidates = buildBackendLookupCandidates(stringBody);

      // Try backend strings dictionary first
      for (const candidate of candidates) {
        const backendTranslated = BACKEND_STRINGS_TRANSLATIONS[language]?.[candidate];
        if (backendTranslated !== undefined) return `${leadingPrefix}${backendTranslated}`;
      }

      // Try partial dictionary replacements for dynamic sentences/lists
      const partialBackendTranslated = translateByBackendDictionaryFragments(stringBody, language);
      if (partialBackendTranslated !== normalizeBackendTranslationKey(stringBody)) {
        return `${leadingPrefix}${partialBackendTranslated}`;
      }

      // Fallback: try literal translations
      const literalTranslated = LITERAL_TRANSLATIONS[language]?.[stringBody];
      if (literalTranslated !== undefined) return literalTranslated;

      // Final fallback: try fallback translations
      if (language !== DEFAULT_LANGUAGE) {
        return `${leadingPrefix}${translateLiteralFallback(stringBody, language)}`;
      }

      // Return original if no translation found
      return backendString;
    },
    [language]
  );

  const value = useMemo(
    () => ({
      language,
      setLanguage,
      supportedLanguages: SUPPORTED_LANGUAGES,
      t,
      translateBackendString,
    }),
    [language, setLanguage, t, translateBackendString]
  );

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
};

export const useI18n = () => {
  const context = useContext(I18nContext);
  if (!context) {
    throw new Error('useI18n debe usarse dentro de I18nProvider');
  }
  return context;
};
