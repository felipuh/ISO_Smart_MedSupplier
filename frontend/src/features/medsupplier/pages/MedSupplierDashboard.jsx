import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  AlertTriangle,
  ClipboardCheck,
  FileText,
  Gauge,
  PackageCheck,
  ShieldCheck,
  Truck,
  Users,
} from 'lucide-react';
import CrudErrorBanner from '../../../components/Common/CrudErrorBanner';
import CrudEmptyState from '../../../components/Common/CrudEmptyState';
import CrudPageHeader from '../../../components/Common/CrudPageHeader';
import { useAuth } from '../../../context/AuthContext';
import { useI18n } from '../../../context/I18nContext';
import medsupplierService from '../../../services/medsupplierService';
import { medsupplierSections } from '../medsupplierSections';
import {
  S3LoadingState,
  S3ResultsSummary,
  S3StatusBadge,
  S3Table,
  S3TableBody,
  S3TableCell,
  S3TableContainer,
  S3TableHead,
  S3TableHeader,
  S3TableRow,
} from '@smart3ai/design-system';

const StatTile = ({ icon: Icon, label, value, tone = 'blue' }) => {
  const tones = {
    blue: 'bg-blue-50 text-blue-700 dark:bg-blue-950/40 dark:text-blue-200',
    emerald: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-200',
    amber: 'bg-amber-50 text-amber-700 dark:bg-amber-950/40 dark:text-amber-200',
    rose: 'bg-rose-50 text-rose-700 dark:bg-rose-950/40 dark:text-rose-200',
    slate: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-200',
  };

  return (
    <div className="enterprise-panel p-4">
      <div className="flex items-center gap-3">
        <span className={`flex h-10 w-10 items-center justify-center rounded-lg ${tones[tone]}`}>
          {React.createElement(Icon, { className: 'h-5 w-5' })}
        </span>
        <div>
          <p className="text-sm text-slate-500 dark:text-slate-400">{label}</p>
          <p className="text-2xl font-semibold text-slate-950 dark:text-white">{value}</p>
        </div>
      </div>
    </div>
  );
};

const FlowStep = ({ label, active }) => (
  <div className={`flex min-h-12 items-center rounded-lg border px-3 py-2 text-sm font-medium ${
    active
      ? 'border-blue-300 bg-blue-50 text-blue-800 dark:border-blue-800 dark:bg-blue-950/40 dark:text-blue-200'
      : 'border-slate-200 bg-white text-slate-600 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-300'
  }`}>
    {label}
  </div>
);

const normalizeValueKey = (value) => String(value || '').trim().toLowerCase().replace(/[\s-]+/g, '_');
const statusTone = (value) => {
  const normalized = normalizeValueKey(value);
  if (['active', 'approved', 'confirmed', 'completed', 'closed', 'delivered', 'exported', 'prepared'].includes(normalized)) return 'success';
  if (['draft', 'planned', 'open', 'under_review', 'pending', 'partial', 'mitigating'].includes(normalized)) return 'info';
  if (['delayed', 'obsolete', 'expired'].includes(normalized)) return 'warning';
  if (['cancelled', 'canceled', 'rejected', 'failed'].includes(normalized)) return 'danger';
  return 'neutral';
};

const MedSupplierDashboard = () => {
  const { currentOrganization } = useAuth();
  const { t } = useI18n();
  const organizationId = currentOrganization?.id;
  const [summary, setSummary] = useState(null);
  const [accounts, setAccounts] = useState([]);
  const [permissions, setPermissions] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadData = useCallback(async () => {
    if (!organizationId) return;
    try {
      setLoading(true);
      setError('');
      const [summaryData, accountData, permissionData] = await Promise.all([
        medsupplierService.getSummary(organizationId),
        medsupplierService.getAccounts(organizationId, { ordering: 'name' }),
        medsupplierService.getPermissions(organizationId),
      ]);
      setSummary(summaryData);
      setAccounts(accountData);
      setPermissions(permissionData);
    } catch (err) {
      console.error('Error loading ISO Smart MedSupplier:', err);
      setError(t('medsupplier.workspace.loadError', { section: t('medsupplier.productName') }));
    } finally {
      setLoading(false);
    }
  }, [organizationId, t]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const flow = useMemo(() => ([
    t('medsupplier.dashboard.flow.account'),
    t('medsupplier.dashboard.flow.meetings'),
    t('medsupplier.dashboard.flow.requirements'),
    t('medsupplier.dashboard.flow.documents'),
    t('medsupplier.dashboard.flow.rfq'),
    t('medsupplier.dashboard.flow.po'),
    t('medsupplier.dashboard.flow.lot'),
    t('medsupplier.dashboard.flow.shipment'),
    t('medsupplier.dashboard.flow.inspection'),
    t('medsupplier.dashboard.flow.capa'),
    t('medsupplier.dashboard.flow.scorecard'),
  ]), [t]);

  const visibleSections = useMemo(() => (
    medsupplierSections.filter((section) => (
      !section.requiresPermission || permissions?.permissions?.[section.requiresPermission]
    ))
  ), [permissions]);

  const translateSectionLabel = (section) => t(`medsupplier.sections.${section.key}.label`, section.label);
  const translateSectionDescription = (section) => t(`medsupplier.sections.${section.key}.description`, section.description);
  const translateValue = (value) => t(`medsupplier.values.${normalizeValueKey(value)}`, value || t('medsupplier.workspace.notAvailable'));

  if (loading) {
    return (
      <div className="enterprise-panel flex min-h-64 items-center justify-center p-8">
        <S3LoadingState variant="section" size="lg" label={t('common.messages.loading')} />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <CrudPageHeader
        title={t('medsupplier.productName')}
        subtitle={t('medsupplier.dashboard.subtitle', { side: permissions?.side || summary?.side || t('medsupplier.dashboard.fallbackSide'), role: permissions?.role || summary?.role || t('medsupplier.dashboard.fallbackRole') })}
      />

      <CrudErrorBanner message={error} onClose={() => setError('')} />

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatTile icon={Users} label={t('medsupplier.dashboard.stats.activeAccounts')} value={summary?.active_accounts ?? 0} tone="blue" />
        <StatTile icon={ClipboardCheck} label={t('medsupplier.dashboard.stats.openActions')} value={summary?.open_actions ?? 0} tone="amber" />
        <StatTile icon={AlertTriangle} label={t('medsupplier.dashboard.stats.qualityEvents')} value={summary?.open_quality_events ?? 0} tone="rose" />
        <StatTile icon={Gauge} label={t('medsupplier.dashboard.stats.averageScorecard')} value={Number(summary?.average_scorecard || 0).toFixed(1)} tone="emerald" />
      </div>

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
        <section className="enterprise-panel p-5 xl:col-span-2">
          <div className="mb-4 flex items-center gap-2">
            <ShieldCheck className="h-5 w-5 text-blue-600 dark:text-blue-300" />
            <h2 className="text-lg font-semibold text-slate-950 dark:text-white">{t('medsupplier.dashboard.flowTitle')}</h2>
          </div>
          <div className="grid grid-cols-2 gap-2 md:grid-cols-4 xl:grid-cols-6">
            {flow.map((step, index) => (
              <FlowStep key={step} label={step} active={index <= 4} />
            ))}
          </div>
        </section>

        <section className="enterprise-panel p-5">
          <div className="mb-4 flex items-center gap-2">
            <FileText className="h-5 w-5 text-blue-600 dark:text-blue-300" />
            <h2 className="text-lg font-semibold text-slate-950 dark:text-white">{t('medsupplier.dashboard.visibilityTitle')}</h2>
          </div>
          <div className="space-y-3">
            <div className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2 dark:bg-slate-800">
              <span className="text-sm text-slate-600 dark:text-slate-300">{t('medsupplier.dashboard.sharedRecords')}</span>
              <span className="font-semibold text-slate-950 dark:text-white">{summary?.shared_records ?? 0}</span>
            </div>
            <div className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2 dark:bg-slate-800">
              <span className="text-sm text-slate-600 dark:text-slate-300">{t('medsupplier.dashboard.privateRecords')}</span>
              <span className="font-semibold text-slate-950 dark:text-white">{summary?.private_records ?? 0}</span>
            </div>
            <div className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2 dark:bg-slate-800">
              <span className="text-sm text-slate-600 dark:text-slate-300">{t('medsupplier.dashboard.rfqs')}</span>
              <span className="font-semibold text-slate-950 dark:text-white">{summary?.rfqs ?? 0}</span>
            </div>
          </div>
        </section>
      </div>

      <section className="enterprise-panel p-5">
        <div className="mb-4 flex items-center gap-2">
          <ShieldCheck className="h-5 w-5 text-blue-600 dark:text-blue-300" />
          <h2 className="text-lg font-semibold text-slate-950 dark:text-white">{t('medsupplier.dashboard.workspaceTitle')}</h2>
        </div>
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-4">
          {visibleSections.filter((section) => section.key !== 'accounts').slice(0, 12).map((section) => {
            const SectionIcon = section.icon;
            return (
              <Link
                key={section.key}
                to={`/medsupplier/${section.key}`}
                className="rounded-lg border border-slate-200 bg-white p-4 transition hover:border-blue-300 hover:bg-blue-50 dark:border-slate-800 dark:bg-slate-950/30 dark:hover:border-blue-800 dark:hover:bg-blue-950/30"
              >
                <SectionIcon className="mb-2 h-5 w-5 text-blue-700 dark:text-blue-200" />
                <p className="font-semibold text-slate-950 dark:text-white">{translateSectionLabel(section)}</p>
                <p className="mt-1 line-clamp-2 text-sm text-slate-500 dark:text-slate-400">{translateSectionDescription(section)}</p>
              </Link>
            );
          })}
        </div>
      </section>

      <section className="enterprise-panel overflow-hidden">
        <div className="enterprise-panel-header flex items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <PackageCheck className="h-5 w-5 text-blue-600 dark:text-blue-300" />
            <h2 className="text-lg font-semibold text-slate-950 dark:text-white">{t('medsupplier.dashboard.customer360Title')}</h2>
          </div>
          <div className="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400">
            <Truck className="h-4 w-4" />
            {t('medsupplier.dashboard.shipmentsInTransit', { count: summary?.shipments_in_transit ?? 0 })}
          </div>
        </div>
        <div className="px-5 pb-3">
          <S3ResultsSummary>
            {accounts.length} {t('medsupplier.dashboard.customer360Title')}
          </S3ResultsSummary>
        </div>
        <S3TableContainer>
          <S3Table>
            <S3TableHead>
              <S3TableRow>
                <S3TableHeader>{t('medsupplier.columns.name')}</S3TableHeader>
                <S3TableHeader>{t('medsupplier.columns.account_code')}</S3TableHeader>
                <S3TableHeader>{t('medsupplier.columns.status')}</S3TableHeader>
                <S3TableHeader>{t('medsupplier.columns.risk_level')}</S3TableHeader>
                <S3TableHeader>{t('medsupplier.columns.visibility')}</S3TableHeader>
              </S3TableRow>
            </S3TableHead>
            <S3TableBody>
              {accounts.map((account) => (
                <S3TableRow key={account.id}>
                  <S3TableCell className="font-medium text-slate-950 dark:text-white">{account.name}</S3TableCell>
                  <S3TableCell>{account.account_code}</S3TableCell>
                  <S3TableCell><S3StatusBadge tone={statusTone(account.status)}>{translateValue(account.status)}</S3StatusBadge></S3TableCell>
                  <S3TableCell>{translateValue(account.risk_level)}</S3TableCell>
                  <S3TableCell>{translateValue(account.visibility)}</S3TableCell>
                </S3TableRow>
              ))}
              {accounts.length === 0 && <CrudEmptyState colSpan={5} message={t('medsupplier.dashboard.emptyAccounts')} />}
            </S3TableBody>
          </S3Table>
        </S3TableContainer>
      </section>
    </div>
  );
};

export default MedSupplierDashboard;
