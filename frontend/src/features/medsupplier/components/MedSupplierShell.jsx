import React, { useEffect, useRef, useState } from 'react';
import { Link, NavLink, Outlet } from 'react-router-dom';
import {
  Activity,
  Bell,
  Check,
  Languages,
  Menu,
  Moon,
  RotateCcw,
  Settings,
  SlidersHorizontal,
  Sun,
  X,
} from 'lucide-react';
import { medsupplierSections } from '../medsupplierSections';
import { useAuth } from '../../../context/AuthContext';
import { useTheme } from '../../../context/ThemeContext';
import { useFontSize } from '../../../context/FontSizeContext';
import { useI18n } from '../../../context/I18nContext';
import UserMenu from '../../../components/Auth/UserMenu';
import VirtualAssistantPanel from '../../../components/Assistant/VirtualAssistantPanel';
import medsupplierService from '../../../services/medsupplierService';
import settingsService from '../../../services/settingsService';

const hasSectionAccess = (section, permissions) => {
  if (!section.requiresPermission) return true;
  return Boolean(permissions?.permissions?.[section.requiresPermission]);
};

const statusClassByType = {
  sent: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300',
  failed: 'bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300',
  skipped: 'bg-slate-100 text-slate-700 dark:bg-slate-700/60 dark:text-slate-200',
  pending: 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300',
};

const MedSupplierShell = () => {
  const { currentOrganization, user } = useAuth();
  const { isDark, resolvedTheme, setTheme, theme, toggleTheme } = useTheme();
  const { decreaseFontSize, increaseFontSize, isMaxLevel, isMinLevel, resetFontSize } = useFontSize();
  const { language, setLanguage, t } = useI18n();
  const [permissions, setPermissions] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [notificationHistory, setNotificationHistory] = useState([]);
  const [notificationsLoading, setNotificationsLoading] = useState(false);
  const [notificationsError, setNotificationsError] = useState(null);
  const notificationsRef = useRef(null);
  const settingsRef = useRef(null);
  const organizationId = currentOrganization?.id;
  const tenantName = currentOrganization?.name || t('header.appSubtitleFallback');

  const eventLabelByType = {
    risk_critical: t('settings.notifications.history.events.riskCritical'),
    risk_high: t('settings.notifications.history.events.riskHigh'),
    objective_deadline: t('settings.notifications.history.events.objectiveDeadline'),
    stakeholder_change: t('settings.notifications.history.events.stakeholderChange'),
    billing_payment_registered: t('settings.notifications.history.events.billingPaymentRegistered'),
    billing_payment_confirmed: t('settings.notifications.history.events.billingPaymentConfirmed'),
    billing_payment_rejected: t('settings.notifications.history.events.billingPaymentRejected'),
    billing_status_changed: t('settings.notifications.history.events.billingStatusChanged'),
    billing_due_reminder: t('settings.notifications.history.events.billingDueReminder'),
  };

  const statusLabelByType = {
    sent: t('settings.notifications.history.status.sent'),
    failed: t('settings.notifications.history.status.failed'),
    skipped: t('settings.notifications.history.status.skipped'),
    pending: t('settings.notifications.history.status.pending'),
  };

  useEffect(() => {
    let mounted = true;
    if (!organizationId) return () => {
      mounted = false;
    };

    medsupplierService.getPermissions(organizationId)
      .then((result) => {
        if (mounted) setPermissions(result);
      })
      .catch((error) => {
        console.error('Error loading MedSupplier permissions:', error);
        if (mounted) setPermissions(null);
      });

    return () => {
      mounted = false;
    };
  }, [organizationId]);

  useEffect(() => {
    const handlePointerDown = (event) => {
      if (notificationsRef.current && !notificationsRef.current.contains(event.target)) {
        setNotificationsOpen(false);
      }
      if (settingsRef.current && !settingsRef.current.contains(event.target)) {
        setSettingsOpen(false);
      }
    };

    const handleKeyDown = (event) => {
      if (event.key === 'Escape') {
        setNotificationsOpen(false);
        setSettingsOpen(false);
        setSidebarOpen(false);
      }
    };

    document.addEventListener('mousedown', handlePointerDown);
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('mousedown', handlePointerDown);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  useEffect(() => {
    if (!notificationsOpen) return;

    const loadNotificationHistory = async () => {
      if (!organizationId) {
        setNotificationHistory([]);
        setNotificationsError(null);
        return;
      }

      setNotificationsLoading(true);
      setNotificationsError(null);
      try {
        const result = await settingsService.getNotificationHistory(organizationId, 8);
        setNotificationHistory(result.results || []);
      } catch (error) {
        console.error('Error loading MedSupplier notifications:', error);
        setNotificationHistory([]);
        setNotificationsError(t('header.notificationsPanel.historyError'));
      } finally {
        setNotificationsLoading(false);
      }
    };

    loadNotificationHistory();
  }, [notificationsOpen, organizationId, t]);

  const visibleSections = medsupplierSections.filter((item) => hasSectionAccess(item, permissions));
  const hasAttentionNotifications = notificationHistory.some((item) => item.status === 'pending' || item.status === 'failed');
  const languageOptions = [
    ['es-LATAM', t('header.languageOptions.es')],
    ['en', t('header.languageOptions.en')],
    ['pt', t('header.languageOptions.pt')],
  ];
  const themeOptions = [
    ['light', t('header.theme.light')],
    ['dark', t('header.theme.dark')],
    ['system', t('header.theme.system')],
  ];
  const switchThemeLabel = isDark ? t('header.theme.switchToLight') : t('header.theme.switchToDark');
  const locale = language === 'es-LATAM' ? 'es-ES' : language;

  const formatWhen = (value) => {
    if (!value) return t('header.notificationsPanel.now');
    try {
      return new Date(value).toLocaleString(locale);
    } catch {
      return value;
    }
  };

  const getSectionLabel = (key, fallback) => (
    t(`navigation.medsupplier.${key}`, '') || t(`medsupplier.sections.${key}.label`, fallback)
  );

  return (
    <div className="min-h-screen bg-slate-50 text-slate-950 dark:bg-slate-950 dark:text-white">
      <a
        href="#medsupplier-content"
        className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[70] focus:rounded-lg focus:bg-blue-800 focus:px-4 focus:py-2 focus:text-sm focus:font-semibold focus:text-white"
      >
        {language === 'en' ? 'Skip to content' : 'Saltar al contenido'}
      </a>
      {sidebarOpen && (
        <button
          type="button"
          className="fixed inset-0 z-30 bg-slate-950/40 lg:hidden"
          aria-hidden="true"
          tabIndex={-1}
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <aside className={`fixed inset-y-0 left-0 z-40 flex w-72 flex-col border-r border-slate-200 bg-white/95 shadow-sm backdrop-blur transition-transform dark:border-slate-800 dark:bg-slate-900/95 ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}`}>
        <div className="border-b border-slate-200 px-5 py-4 dark:border-slate-800">
          <Link to="/medsupplier" className="flex items-center gap-3" onClick={() => setSidebarOpen(false)}>
            <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-blue-800 text-white shadow-sm">
              <Activity className="h-5 w-5" />
            </span>
            <span className="min-w-0">
              <span className="block truncate text-base font-semibold tracking-normal">{t('header.appTitle')}</span>
              <span className="mt-1 block truncate text-xs text-slate-500 dark:text-slate-400">{tenantName}</span>
            </span>
          </Link>
          <div className="mt-4 rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-xs font-semibold text-emerald-800 dark:border-emerald-900/60 dark:bg-emerald-950/30 dark:text-emerald-300">
            {t('medsupplier.productName')}
          </div>
        </div>

        <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-4">
          {visibleSections.map((item) => {
            const Icon = item.icon;
            const to = item.key === 'accounts' ? '/medsupplier/accounts' : `/medsupplier/${item.key}`;
            return (
              <NavLink
                key={item.key}
                to={to}
                onClick={() => setSidebarOpen(false)}
                className={({ isActive }) => `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition ${
                  isActive
                    ? 'bg-blue-50 text-blue-800 ring-1 ring-blue-100 dark:bg-blue-950/40 dark:text-blue-100 dark:ring-blue-900/50'
                    : 'text-slate-600 hover:bg-slate-100 hover:text-slate-950 dark:text-slate-300 dark:hover:bg-slate-800 dark:hover:text-white'
                }`}
              >
                <Icon className="h-4 w-4 shrink-0" />
                <span className="truncate">{getSectionLabel(item.key, item.label)}</span>
              </NavLink>
            );
          })}
        </nav>

        <div className="border-t border-slate-200 p-4 dark:border-slate-800">
          <p className="truncate text-sm font-semibold">{currentOrganization?.name || t('auth.userMenu.noOrganization')}</p>
          <p className="truncate text-xs text-slate-500 dark:text-slate-400">{user?.email}</p>
          <p className="mt-1 truncate text-xs text-slate-500 dark:text-slate-400">{permissions?.role || t('navigation.medsupplier.cockpit')}</p>
        </div>
      </aside>

      <div className="lg:pl-72">
        <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/95 px-3 py-3 shadow-sm backdrop-blur-xl dark:border-slate-800 dark:bg-slate-950/90 sm:px-6">
          <div className="flex items-center justify-between gap-3">
            <div className="flex min-w-0 items-center gap-3">
              <button
                type="button"
                onClick={() => setSidebarOpen((value) => !value)}
                className="rounded-lg border border-slate-300 bg-white p-2 text-slate-600 shadow-sm hover:border-slate-400 hover:bg-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200 dark:hover:bg-slate-800 lg:hidden"
                aria-label={sidebarOpen ? t('header.navigation.close') : t('header.navigation.open')}
                aria-expanded={sidebarOpen}
              >
                {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
              </button>
              <div className="min-w-0">
                <p className="truncate text-sm font-semibold text-slate-900 dark:text-slate-100">{t('header.productStatus')}</p>
                <p className="hidden truncate text-xs text-slate-500 dark:text-slate-400 sm:block">{t('header.productGovernance')}</p>
              </div>
            </div>

            <div className="flex shrink-0 items-center gap-1 sm:gap-2">
              <button
                type="button"
                onClick={toggleTheme}
                className="rounded-lg border border-slate-300 bg-white p-2 text-slate-600 shadow-sm hover:border-slate-400 hover:bg-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200 dark:hover:bg-slate-800"
                aria-label={switchThemeLabel}
                title={switchThemeLabel}
              >
                {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
              </button>

              <div className="hidden items-center gap-1 rounded-lg border border-slate-300 bg-white px-1 py-1 shadow-sm dark:border-slate-700 dark:bg-slate-900 sm:flex" role="group" aria-label={t('header.accessibility.fontSizeLabel')}>
                <button
                  type="button"
                  onClick={decreaseFontSize}
                  disabled={isMinLevel}
                  className="rounded-md px-2 py-1.5 text-sm font-semibold text-slate-600 hover:bg-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:cursor-not-allowed disabled:opacity-40 dark:text-slate-200 dark:hover:bg-slate-800"
                  aria-label={t('header.accessibility.decreaseFont')}
                  title={t('header.accessibility.decreaseFont')}
                >
                  A-
                </button>
                <button
                  type="button"
                  onClick={resetFontSize}
                  className="rounded-md p-1.5 text-slate-600 hover:bg-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:text-slate-200 dark:hover:bg-slate-800"
                  aria-label={t('header.accessibility.resetFont')}
                  title={t('header.accessibility.resetFont')}
                >
                  <RotateCcw className="h-4 w-4" />
                </button>
                <button
                  type="button"
                  onClick={increaseFontSize}
                  disabled={isMaxLevel}
                  className="rounded-md px-2 py-1.5 text-sm font-semibold text-slate-600 hover:bg-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:cursor-not-allowed disabled:opacity-40 dark:text-slate-200 dark:hover:bg-slate-800"
                  aria-label={t('header.accessibility.increaseFont')}
                  title={t('header.accessibility.increaseFont')}
                >
                  A+
                </button>
              </div>

              <label className="hidden items-center gap-2 rounded-lg border border-slate-300 bg-white px-2 py-1.5 text-xs font-medium text-slate-600 shadow-sm dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200 md:flex">
                <Languages className="h-4 w-4" aria-hidden="true" />
                <span className="sr-only">{t('header.languageLabel')}</span>
                <select
                  aria-label={t('header.languageLabel')}
                  value={language}
                  onChange={(event) => setLanguage(event.target.value)}
                  className="bg-transparent text-xs font-semibold focus:outline-none"
                >
                  {languageOptions.map(([code, label]) => (
                    <option key={code} value={code}>{label}</option>
                  ))}
                </select>
              </label>

              <div className="relative" ref={notificationsRef}>
                <button
                  type="button"
                  onClick={() => {
                    setNotificationsOpen((value) => !value);
                    setSettingsOpen(false);
                  }}
                  className="relative rounded-lg border border-slate-300 bg-white p-2 text-slate-600 shadow-sm hover:border-slate-400 hover:bg-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200 dark:hover:bg-slate-800"
                  aria-label={notificationsOpen ? t('header.notificationsPanel.close') : t('header.notificationsPanel.open')}
                  aria-haspopup="menu"
                  aria-expanded={notificationsOpen}
                  aria-controls="medsupplier-notifications-panel"
                  title={t('header.notifications')}
                >
                  <Bell className="h-4 w-4" />
                  {hasAttentionNotifications && <span className="absolute right-1 top-1 h-2 w-2 rounded-full bg-red-500" />}
                </button>

                {notificationsOpen && (
                  <div
                    id="medsupplier-notifications-panel"
                    role="menu"
                    aria-label={t('header.notificationsPanel.label')}
                    className="absolute right-0 mt-2 w-[22rem] max-w-[calc(100vw-1.5rem)] overflow-hidden rounded-lg border border-slate-200 bg-white shadow-xl dark:border-slate-700 dark:bg-slate-900"
                  >
                    <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3 dark:border-slate-700">
                      <h2 className="text-sm font-semibold">{t('header.notifications')}</h2>
                      <span className="text-xs text-slate-500 dark:text-slate-400">{notificationHistory.length}</span>
                    </div>
                    <div className="max-h-80 overflow-y-auto">
                      {notificationsLoading && <div className="px-4 py-5 text-sm text-slate-500 dark:text-slate-400">{t('header.notificationsPanel.loading')}</div>}
                      {!notificationsLoading && notificationsError && <div className="px-4 py-5 text-sm text-red-600 dark:text-red-300">{notificationsError}</div>}
                      {!notificationsLoading && !notificationsError && notificationHistory.length === 0 && (
                        <div className="px-4 py-5 text-sm text-slate-500 dark:text-slate-400">{t('header.notificationsPanel.empty')}</div>
                      )}
                      {!notificationsLoading && !notificationsError && notificationHistory.map((item) => (
                        <div key={item.id} className="border-b border-slate-100 px-4 py-3 last:border-b-0 dark:border-slate-800">
                          <div className="flex items-start justify-between gap-3">
                            <div className="min-w-0">
                              <p className="truncate text-sm font-medium">{eventLabelByType[item.event_type] || item.event_type}</p>
                              <p className="truncate text-xs text-slate-500 dark:text-slate-400">{item.subject}</p>
                              <p className="mt-1 text-xs text-slate-400 dark:text-slate-500">
                                {Array.isArray(item.recipients) && item.recipients.length > 0 ? item.recipients.join(', ') : t('header.notificationsPanel.noRecipients')}
                              </p>
                            </div>
                            <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${statusClassByType[item.status] || statusClassByType.pending}`}>
                              {statusLabelByType[item.status] || item.status}
                            </span>
                          </div>
                          <p className="mt-2 text-[11px] text-slate-400 dark:text-slate-500">{formatWhen(item.sent_at || item.created_at)}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div className="relative" ref={settingsRef}>
                <button
                  type="button"
                  onClick={() => {
                    setSettingsOpen((value) => !value);
                    setNotificationsOpen(false);
                  }}
                  className="rounded-lg border border-slate-300 bg-white p-2 text-slate-600 shadow-sm hover:border-slate-400 hover:bg-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200 dark:hover:bg-slate-800"
                  aria-label={settingsOpen ? t('header.settingsMenu.close') : t('header.settingsMenu.open')}
                  aria-haspopup="menu"
                  aria-expanded={settingsOpen}
                  aria-controls="medsupplier-settings-menu"
                  title={t('header.settings')}
                >
                  <Settings className="h-4 w-4" />
                </button>

                {settingsOpen && (
                  <div
                    id="medsupplier-settings-menu"
                    role="menu"
                    aria-label={t('header.settingsMenu.label')}
                    className="absolute right-0 mt-2 w-80 max-w-[calc(100vw-1.5rem)] rounded-lg border border-slate-200 bg-white p-3 shadow-xl dark:border-slate-700 dark:bg-slate-900"
                  >
                    <div className="mb-3 flex items-center gap-2 px-1">
                      <SlidersHorizontal className="h-4 w-4 text-blue-600 dark:text-blue-300" />
                      <h2 className="text-sm font-semibold">{t('header.settingsMenu.title')}</h2>
                    </div>

                    <div className="space-y-4">
                      <section>
                        <p className="mb-2 text-xs font-semibold uppercase text-slate-500 dark:text-slate-400">{t('header.settingsMenu.visualPreferences')}</p>
                        <div className="grid grid-cols-3 gap-1">
                          {themeOptions.map(([code, label]) => (
                            <button
                              key={code}
                              type="button"
                              onClick={() => setTheme(code)}
                              className={`flex items-center justify-center gap-1 rounded-md border px-2 py-2 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 ${theme === code ? 'border-blue-600 bg-blue-50 text-blue-700 dark:border-blue-400 dark:bg-blue-500/20 dark:text-blue-200' : 'border-slate-200 text-slate-600 hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800'}`}
                              aria-pressed={theme === code}
                            >
                              {theme === code && <Check className="h-3 w-3" />}
                              {label}
                            </button>
                          ))}
                        </div>
                        <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">{resolvedTheme === 'dark' ? t('header.theme.dark') : t('header.theme.light')}</p>
                      </section>

                      <section className="sm:hidden">
                        <p className="mb-2 text-xs font-semibold uppercase text-slate-500 dark:text-slate-400">{t('header.settingsMenu.accessibility')}</p>
                        <div className="flex gap-1">
                          <button type="button" onClick={decreaseFontSize} disabled={isMinLevel} className="flex-1 rounded-md border border-slate-200 px-2 py-2 text-sm font-semibold disabled:opacity-40 dark:border-slate-700">A-</button>
                          <button type="button" onClick={resetFontSize} className="flex-1 rounded-md border border-slate-200 px-2 py-2 text-sm font-semibold dark:border-slate-700">{t('header.accessibility.resetFont')}</button>
                          <button type="button" onClick={increaseFontSize} disabled={isMaxLevel} className="flex-1 rounded-md border border-slate-200 px-2 py-2 text-sm font-semibold disabled:opacity-40 dark:border-slate-700">A+</button>
                        </div>
                      </section>

                      <section>
                        <p className="mb-2 text-xs font-semibold uppercase text-slate-500 dark:text-slate-400">{t('header.settingsMenu.language')}</p>
                        <select
                          aria-label={t('header.languageLabel')}
                          value={language}
                          onChange={(event) => setLanguage(event.target.value)}
                          className="w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
                        >
                          {languageOptions.map(([code, label]) => (
                            <option key={code} value={code}>{label}</option>
                          ))}
                        </select>
                      </section>
                    </div>

                    <div className="mt-4 grid grid-cols-2 gap-2 border-t border-slate-200 pt-3 dark:border-slate-700">
                      <Link to="/settings" onClick={() => setSettingsOpen(false)} className="rounded-md bg-blue-600 px-3 py-2 text-center text-xs font-semibold text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500">
                        {t('header.settingsMenu.goToSettings')}
                      </Link>
                      <Link to="/profile" onClick={() => setSettingsOpen(false)} className="rounded-md border border-slate-200 px-3 py-2 text-center text-xs font-semibold text-slate-700 hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800">
                        {t('header.settingsMenu.goToProfile')}
                      </Link>
                    </div>
                  </div>
                )}
              </div>

              <UserMenu />
            </div>
          </div>
        </header>

        <main id="medsupplier-content" className="px-4 py-5 sm:px-6 lg:px-8 lg:py-8" tabIndex={-1}>
          <div className="mx-auto w-full max-w-[1480px]">
            <Outlet />
          </div>
        </main>
        <VirtualAssistantPanel />
      </div>
    </div>
  );
};

export default MedSupplierShell;
