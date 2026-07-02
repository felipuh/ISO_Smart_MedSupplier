import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { Building2, KeyRound, LockKeyhole, Pencil, Plus, RefreshCw, ShieldCheck, Trash2 } from 'lucide-react';
import CrudEmptyState from '../../../components/Common/CrudEmptyState';
import CrudErrorBanner from '../../../components/Common/CrudErrorBanner';
import Modal from '../../../components/Common/Modal';
import { useAuth } from '../../../context/AuthContext';
import { useI18n } from '../../../context/I18nContext';
import medsupplierService from '../../../services/medsupplierService';
import { getMedSupplierSection, medsupplierSections } from '../medsupplierSections';

const normalizeValueKey = (value) => String(value || '').trim().toLowerCase().replace(/[\s-]+/g, '_');

const formatCell = (value, { locale, t, translateValue }) => {
  if (value === null || value === undefined || value === '') return t('medsupplier.workspace.notAvailable');
  if (typeof value === 'number') return value.toLocaleString(locale);
  if (typeof value === 'boolean') return value ? t('medsupplier.workspace.booleanYes') : t('medsupplier.workspace.booleanNo');
  if (typeof value === 'string' && value.includes('T') && value.endsWith('Z')) {
    return new Date(value).toLocaleString(locale);
  }
  const translated = translateValue(value);
  if (translated !== value) return translated;
  return String(value);
};

const statusLabel = (value, t) => (value ? t('medsupplier.integration.statusReady') : t('medsupplier.integration.statusAttention'));

const formatInputValue = (field, value) => {
  if (value === null || value === undefined) return '';
  if (field.type === 'file') return '';
  if (field.type === 'multirelation') {
    return Array.isArray(value) ? value.map(String) : [];
  }
  if (field.type === 'datetime-local' && typeof value === 'string') {
    return value.slice(0, 16);
  }
  return value;
};

const buildInitialForm = (fields, record = null) => (
  fields.reduce((values, field) => {
    const fallback = field.defaultValue ?? (field.type === 'checkbox' ? false : field.type === 'multirelation' ? [] : '');
    values[field.name] = formatInputValue(field, record?.[field.name] ?? fallback);
    return values;
  }, {})
);

const normalizePayload = (fields, form) => (
  fields.reduce((payload, field) => {
    const value = form[field.name];
    if (field.omitWhenEmpty && value === '') {
      return payload;
    }
    if (field.type === 'file') {
      if (value) {
        payload[field.name] = value;
      }
      return payload;
    }
    if (['date', 'datetime-local', 'relation'].includes(field.type) && value === '') {
      payload[field.name] = null;
      return payload;
    }
    if (field.type === 'multirelation') {
      payload[field.name] = Array.isArray(value) ? value : [];
      return payload;
    }
    payload[field.name] = value;
    return payload;
  }, {})
);

const extractApiError = (error, fallback) => {
  const data = error?.response?.data;
  if (!data) return fallback;
  if (typeof data === 'string') return data;
  if (data.detail) return data.detail;
  const firstKey = Object.keys(data)[0];
  const firstValue = data[firstKey];
  if (Array.isArray(firstValue)) return `${firstKey}: ${firstValue.join(', ')}`;
  if (typeof firstValue === 'string') return `${firstKey}: ${firstValue}`;
  return fallback;
};

const formatRelationLabel = (item, fields = ['name']) => (
  fields
    .map((field) => item[field])
    .filter(Boolean)
    .join(' - ') || `#${item.id}`
);

const getWorkflowDisabledReason = (workflowAction, item, t) => {
  const statusReason = workflowAction.disabledStatuses?.[item.status];
  if (statusReason) return t(`medsupplier.workflow.disabled.${statusReason}`, statusReason);

  if (workflowAction.disableWhenExpired && item.valid_until) {
    const validUntil = new Date(`${item.valid_until}T00:00:00`);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    if (validUntil < today) {
      return workflowAction.expiredReason ? t(`medsupplier.workflow.disabled.${workflowAction.expiredReason}`, workflowAction.expiredReason) : t('medsupplier.workspace.expiredRecord');
    }
  }

  if (workflowAction.requiredField && !String(item[workflowAction.requiredField] || '').trim()) {
    return workflowAction.requiredFieldReason ? t(`medsupplier.workflow.disabled.${workflowAction.requiredFieldReason}`, workflowAction.requiredFieldReason) : t('medsupplier.workspace.missingRequiredInfo');
  }

  return '';
};

const RecordForm = ({ fields, form, lookupOptions, onChange, onSubmit, onCancel, saving, submitLabel, t, translateFieldLabel, translateOptionLabel }) => (
  <form className="space-y-5" onSubmit={onSubmit}>
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
      {fields.map((field) => {
        if (field.type === 'checkbox') {
          return (
            <label
              key={field.name}
              className="flex min-h-11 items-center gap-3 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-700 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200"
            >
              <input
                type="checkbox"
                checked={Boolean(form[field.name])}
                onChange={(event) => onChange(field.name, event.target.checked)}
                className="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
              />
              {translateFieldLabel(field)}
            </label>
          );
        }

        return (
          <label key={field.name} className="form-label-muted">
            {translateFieldLabel(field)}
            {field.required ? <span className="text-red-500"> *</span> : null}
            {field.type === 'select' || field.type === 'relation' || field.type === 'multirelation' ? (
              <select
                required={field.required}
                value={form[field.name] ?? ''}
                multiple={field.type === 'multirelation'}
                onChange={(event) => {
                  if (field.type === 'multirelation') {
                    onChange(field.name, Array.from(event.target.selectedOptions).map((option) => option.value));
                    return;
                  }
                  onChange(field.name, event.target.value);
                }}
                className="field-control"
              >
                {field.type === 'relation' || field.type === 'multirelation' ? (
                  <>
                    {field.type === 'relation' ? <option value="">{t('medsupplier.workspace.selectOption')}</option> : null}
                    {(lookupOptions[field.name] || []).map((item) => (
                      <option key={item.id} value={item.id}>
                        {formatRelationLabel(item, field.optionFields)}
                      </option>
                    ))}
                  </>
                ) : (
                  (field.options || []).map(([value, label]) => (
                    <option key={value} value={value}>{translateOptionLabel(value, label)}</option>
                  ))
                )}
              </select>
            ) : field.type === 'textarea' ? (
              <textarea
                required={field.required}
                value={form[field.name] ?? ''}
                onChange={(event) => onChange(field.name, event.target.value)}
                className="field-control min-h-24"
              />
            ) : field.type === 'file' ? (
              <input
                type="file"
                required={field.required}
                onChange={(event) => onChange(field.name, event.target.files?.[0] || '')}
                className="field-control"
              />
            ) : (
              <input
                type={field.type || 'text'}
                required={field.required}
                value={form[field.name] ?? ''}
                onChange={(event) => onChange(field.name, event.target.value)}
                step={field.step}
                min={field.min}
                max={field.max}
                className="field-control"
              />
            )}
          </label>
        );
      })}
    </div>

    <div className="flex justify-end gap-3 border-t border-slate-200 pt-4 dark:border-slate-800">
      <button type="button" onClick={onCancel} className="btn-secondary" disabled={saving}>
        {t('medsupplier.workspace.cancel')}
      </button>
      <button type="submit" className="btn-primary" disabled={saving}>
        {saving ? t('medsupplier.workspace.saving') : submitLabel}
      </button>
    </div>
  </form>
);

const hasPermission = (permissions, permissionName) => {
  if (!permissionName) return true;
  return Boolean(permissions?.permissions?.[permissionName]);
};

const filterPermittedFields = (fields, permissions) => (
  (fields || []).filter((field) => hasPermission(permissions, field.requiresPermission))
);

const ProductModePanel = ({ status, loading, onRefresh, t }) => (
  <div className="space-y-4">
    <section className="rounded-lg border border-blue-200 bg-blue-50 p-5 dark:border-blue-900 dark:bg-blue-950/30">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="mb-2 flex items-center gap-2 text-blue-800 dark:text-blue-200">
            <ShieldCheck className="h-5 w-5" />
            <h2 className="text-lg font-semibold">{t('medsupplier.integration.title')}</h2>
          </div>
          <p className="max-w-4xl text-sm text-blue-950 dark:text-blue-100">
            {t('medsupplier.integration.description')}
          </p>
        </div>
        <button
          type="button"
          onClick={onRefresh}
          className="flex items-center gap-2 rounded-lg border border-blue-300 px-3 py-2 text-sm font-medium text-blue-800 hover:bg-blue-100 dark:border-blue-800 dark:text-blue-100 dark:hover:bg-blue-900/40"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          {t('medsupplier.integration.refresh')}
        </button>
      </div>
    </section>

    <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
      <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div className="mb-3 flex items-center gap-2 text-emerald-700 dark:text-emerald-200">
          <KeyRound className="h-5 w-5" />
          <h3 className="font-semibold">{t('medsupplier.integration.identityTitle')}</h3>
        </div>
        <p className="text-sm text-slate-600 dark:text-slate-300">
          {t('medsupplier.integration.adminAppsStatus')}: <strong>{statusLabel(status?.adminapps?.available, t)}</strong>
        </p>
        <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">
          {t('medsupplier.integration.identityDescription')}
        </p>
      </div>
      <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div className="mb-3 flex items-center gap-2 text-blue-700 dark:text-blue-200">
          <Building2 className="h-5 w-5" />
          <h3 className="font-semibold">{t('medsupplier.integration.enablementTitle')}</h3>
        </div>
        <p className="text-sm text-slate-600 dark:text-slate-300">
          {t('medsupplier.integration.module')}: <strong>{statusLabel(status?.entitlement?.enabled, t)}</strong>
        </p>
        <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">
          {t('medsupplier.integration.commercialCode')}: <strong>{status?.module_code || 'MEDSUPPLIER'}</strong>
        </p>
      </div>
      <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div className="mb-3 flex items-center gap-2 text-amber-700 dark:text-amber-200">
          <LockKeyhole className="h-5 w-5" />
          <h3 className="font-semibold">{t('medsupplier.integration.separationTitle')}</h3>
        </div>
        <p className="text-sm text-slate-600 dark:text-slate-300">
          {t('medsupplier.integration.mode')}: <strong>{status?.product_mode || 'integrated'}</strong>
        </p>
        <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">
          {t('medsupplier.integration.separationDescription')}
        </p>
      </div>
    </div>
  </div>
);

const PrivateCockpitPanel = ({ data, loading, onRefresh, t, formatValue }) => {
  if (loading) {
    return (
      <div className="flex justify-center p-8">
        <div className="h-10 w-10 animate-spin rounded-full border-b-2 border-blue-500" />
      </div>
    );
  }

  const opportunity = data?.opportunities || {};
  const finance = data?.finance || {};
  const aging = data?.aging || {};

  return (
    <div className="space-y-4">
      <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div className="flex items-center justify-between gap-3">
          <div>
            <h2 className="text-lg font-semibold text-slate-950 dark:text-white">{t('medsupplier.cockpit.title')}</h2>
            <p className="text-sm text-slate-500 dark:text-slate-400">{t('medsupplier.cockpit.subtitle')}</p>
          </div>
          <button type="button" onClick={onRefresh} className="btn-secondary">{t('medsupplier.cockpit.refresh')}</button>
        </div>
      </section>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        {[
          [t('medsupplier.cockpit.rfqs'), opportunity.rfqs ?? 0],
          [t('medsupplier.cockpit.pendingQuotes'), opportunity.quotes_pending ?? 0],
          [t('medsupplier.cockpit.openOrders'), opportunity.orders_open ?? 0],
          [t('medsupplier.cockpit.averageMargin'), `${finance.average_margin ?? '0.00'}%`],
          [t('medsupplier.cockpit.commissions'), finance.commission_total ?? '0.00'],
          [t('medsupplier.cockpit.expiredQuotes'), aging.expired_quotes ?? 0],
        ].map(([label, value]) => (
          <div key={label} className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
            <p className="text-sm text-slate-500 dark:text-slate-400">{label}</p>
            <p className="mt-1 text-2xl font-semibold text-slate-950 dark:text-white">{value}</p>
          </div>
        ))}
      </div>

      <section className="rounded-lg border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div className="border-b border-slate-200 px-5 py-4 dark:border-slate-800">
          <h3 className="font-semibold text-slate-950 dark:text-white">{t('medsupplier.cockpit.forecastTitle')}</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-100 dark:bg-slate-800/60">
              <tr>
                {['Quote', t('medsupplier.columns.status'), t('medsupplier.columns.total_amount'), t('medsupplier.fields.margin'), t('medsupplier.fields.forecast_probability'), t('medsupplier.fields.valid_until')].map((label) => (
                  <th key={label} className="px-5 py-3 text-left text-xs font-medium uppercase text-slate-600 dark:text-slate-300">{label}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
              {(data?.forecast || []).map((item) => (
                <tr key={item.id}>
                  <td className="px-5 py-4 text-sm text-slate-700 dark:text-slate-200">{item.quote_number}</td>
                  <td className="px-5 py-4 text-sm text-slate-700 dark:text-slate-200">{formatValue(item.status)}</td>
                  <td className="px-5 py-4 text-sm text-slate-700 dark:text-slate-200">{item.total_amount}</td>
                  <td className="px-5 py-4 text-sm text-slate-700 dark:text-slate-200">{item.margin}</td>
                  <td className="px-5 py-4 text-sm text-slate-700 dark:text-slate-200">{item.forecast_probability}%</td>
                  <td className="px-5 py-4 text-sm text-slate-700 dark:text-slate-200">{formatValue(item.valid_until)}</td>
                </tr>
              ))}
              {(!data?.forecast || data.forecast.length === 0) && <CrudEmptyState colSpan={6} message={t('medsupplier.cockpit.emptyForecast')} />}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
};

const MedSupplierWorkspace = () => {
  const { sectionKey = 'accounts' } = useParams();
  const section = getMedSupplierSection(sectionKey);
  const { currentOrganization } = useAuth();
  const { language, t } = useI18n();
  const organizationId = currentOrganization?.id;
  const [items, setItems] = useState([]);
  const [count, setCount] = useState(0);
  const [loading, setLoading] = useState(Boolean(section.resource));
  const [integrationStatus, setIntegrationStatus] = useState(null);
  const [integrationLoading, setIntegrationLoading] = useState(false);
  const [permissions, setPermissions] = useState(null);
  const [cockpitData, setCockpitData] = useState(null);
  const [cockpitLoading, setCockpitLoading] = useState(false);
  const [error, setError] = useState('');
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingRecord, setEditingRecord] = useState(null);
  const permittedFields = useMemo(() => filterPermittedFields(section.formFields || [], permissions), [section.formFields, permissions]);
  const [form, setForm] = useState(() => buildInitialForm(permittedFields));
  const [saving, setSaving] = useState(false);
  const [lookupOptions, setLookupOptions] = useState({});
  const canMutate = Boolean(section.resource && permittedFields.length && permissions?.permissions?.can_mutate);
  const locale = language === 'es-LATAM' ? 'es-ES' : language === 'pt' ? 'pt-BR' : 'en-US';
  const sectionLabel = t(`medsupplier.sections.${section.key}.label`, section.label);
  const sectionDescription = t(`medsupplier.sections.${section.key}.description`, section.description);
  const translateSectionLabel = (item) => t(`medsupplier.sections.${item.key}.label`, item.label);
  const translateSectionDescription = (item) => t(`medsupplier.sections.${item.key}.description`, item.description);
  const translateFieldLabel = (field) => t(`medsupplier.fields.${field.name}`, field.label);
  const translateColumnLabel = (field, fallback) => t(`medsupplier.columns.${field}`, fallback);
  const translateOptionLabel = (value, fallback) => t(`medsupplier.values.${normalizeValueKey(value)}`, fallback);
  const translateWorkflowAction = (workflowAction) => t(`medsupplier.workflow.${workflowAction.labelKey || workflowAction.action}`, workflowAction.label);
  const translateWorkflowConfirm = (workflowAction) => (
    workflowAction.confirmKey ? t(`medsupplier.workflow.confirms.${workflowAction.confirmKey}`) : t('medsupplier.workspace.workflowConfirm', { action: translateWorkflowAction(workflowAction) })
  );
  const translateValue = (value) => t(`medsupplier.values.${normalizeValueKey(value)}`, value);
  const formatValue = (value) => formatCell(value, { locale, t, translateValue });

  const loadData = useCallback(async () => {
    if (!organizationId || !section.resource) {
      setItems([]);
      setCount(0);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError('');
      const result = await medsupplierService.list(section.resource, organizationId);
      setItems(result.items);
      setCount(result.count);
    } catch (err) {
      console.error(`Error loading MedSupplier ${section.resource}:`, err);
      setError(t('medsupplier.workspace.loadError', { section: sectionLabel }));
    } finally {
      setLoading(false);
    }
  }, [organizationId, section.resource, sectionLabel, t]);

  const loadPermissions = useCallback(async () => {
    if (!organizationId) return;
    try {
      const result = await medsupplierService.getPermissions(organizationId);
      setPermissions(result);
    } catch (err) {
      console.error('Error loading MedSupplier permissions:', err);
      setPermissions(null);
    }
  }, [organizationId]);

  const loadIntegrationStatus = useCallback(async () => {
    if (!organizationId || section.key !== 'integration') return;

    try {
      setIntegrationLoading(true);
      setError('');
      const result = await medsupplierService.getIntegrationStatus(organizationId);
      setIntegrationStatus(result);
    } catch (err) {
      console.error('Error loading MedSupplier integration status:', err);
      setError(t('medsupplier.workspace.integrationError'));
    } finally {
      setIntegrationLoading(false);
    }
  }, [organizationId, section.key, t]);

  const loadPrivateCockpit = useCallback(async () => {
    if (!organizationId || section.key !== 'cockpit') return;
    try {
      setCockpitLoading(true);
      setError('');
      const result = await medsupplierService.getPrivateCockpit(organizationId);
      setCockpitData(result);
    } catch (err) {
      console.error('Error loading private cockpit:', err);
      setError(extractApiError(err, t('medsupplier.workspace.cockpitAccessError')));
      setCockpitData(null);
    } finally {
      setCockpitLoading(false);
    }
  }, [organizationId, section.key, t]);

  useEffect(() => {
    loadPermissions();
  }, [loadPermissions]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  useEffect(() => {
    loadIntegrationStatus();
  }, [loadIntegrationStatus]);

  useEffect(() => {
    loadPrivateCockpit();
  }, [loadPrivateCockpit]);

  useEffect(() => {
    const relationFields = permittedFields.filter((field) => ['relation', 'multirelation'].includes(field.type));
    if (!organizationId || relationFields.length === 0) {
      setLookupOptions({});
      return;
    }

    let mounted = true;
    const loadLookups = async () => {
      try {
        const entries = await Promise.all(
          relationFields.map(async (field) => {
            const result = await medsupplierService.list(
              field.resource,
              organizationId,
              field.ordering ? { ordering: field.ordering } : {}
            );
            return [field.name, result.items];
          })
        );
        if (mounted) {
          setLookupOptions(Object.fromEntries(entries));
        }
      } catch (err) {
        if (mounted) {
          setLookupOptions({});
          setError(extractApiError(err, t('medsupplier.workspace.relatedDataError')));
        }
      }
    };

    loadLookups();
    return () => {
      mounted = false;
    };
  }, [organizationId, permittedFields, t]);

  useEffect(() => {
    setIsFormOpen(false);
    setEditingRecord(null);
    setForm(buildInitialForm(permittedFields));
  }, [section.key, permittedFields]);

  const relatedSections = useMemo(() => (
    medsupplierSections
      .filter((item) => item.key !== section.key)
      .filter((item) => hasPermission(permissions, item.requiresPermission))
      .slice(0, 4)
  ), [section.key, permissions]);

  const Icon = section.icon;

  const openCreateForm = () => {
    setEditingRecord(null);
    setForm(buildInitialForm(permittedFields));
    setIsFormOpen(true);
  };

  const openEditForm = (record) => {
    setEditingRecord(record);
    setForm(buildInitialForm(permittedFields, record));
    setIsFormOpen(true);
  };

  const closeForm = () => {
    if (saving) return;
    setIsFormOpen(false);
    setEditingRecord(null);
  };

  const updateFormValue = (name, value) => {
    setForm((current) => ({ ...current, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!organizationId || !section.resource || !permittedFields.length) return;

    try {
      setSaving(true);
      setError('');
      const payload = normalizePayload(permittedFields, form);
      if (editingRecord) {
        await medsupplierService.update(section.resource, organizationId, editingRecord.id, payload);
      } else {
        await medsupplierService.create(section.resource, organizationId, payload);
      }
      setIsFormOpen(false);
      setEditingRecord(null);
      await loadData();
    } catch (err) {
      setError(extractApiError(err, t('medsupplier.workspace.saveError', { section: sectionLabel })));
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (record) => {
    if (!organizationId || !section.resource) return;
    const label = record.name || record.account_code || record.id;
    const confirmed = window.confirm(t('medsupplier.workspace.deleteConfirm', { label }));
    if (!confirmed) return;

    try {
      setSaving(true);
      setError('');
      await medsupplierService.remove(section.resource, organizationId, record.id);
      await loadData();
    } catch (err) {
      setError(extractApiError(err, t('medsupplier.workspace.deleteError', { section: sectionLabel })));
    } finally {
      setSaving(false);
    }
  };

  const handleWorkflowAction = async (record, workflowAction) => {
    if (!organizationId || !section.resource) return;
    const confirmed = window.confirm(translateWorkflowConfirm(workflowAction));
    if (!confirmed) return;
    const requiresReason = ['approve', 'reject', 'close'].includes(workflowAction.action);
    const reason = requiresReason ? window.prompt(t('medsupplier.workspace.reasonPrompt')) : '';
    if (requiresReason && !String(reason || '').trim()) {
      setError(t('medsupplier.workspace.reasonRequired'));
      return;
    }

    try {
      setSaving(true);
      setError('');
      await medsupplierService.runWorkflowAction(section.resource, organizationId, record.id, workflowAction.action, { reason });
      await loadData();
    } catch (err) {
      setError(extractApiError(err, t('medsupplier.workspace.workflowError', { action: translateWorkflowAction(workflowAction) })));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="mb-2 flex items-center gap-2 text-sm font-medium text-blue-700 dark:text-blue-200">
            <Icon className="h-4 w-4" />
            {t('medsupplier.productName')}
          </div>
          <h1 className="text-3xl font-bold text-slate-950 dark:text-white">{sectionLabel}</h1>
          <p className="mt-1 max-w-3xl text-slate-600 dark:text-slate-300">{sectionDescription}</p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          {canMutate ? (
            <button
              type="button"
              onClick={openCreateForm}
              disabled={!organizationId}
              className="btn-primary inline-flex items-center gap-2 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <Plus className="h-4 w-4" />
              {t('medsupplier.workspace.newRecord')}
            </button>
          ) : null}
          <div className="rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm shadow-sm dark:border-slate-800 dark:bg-slate-900">
            <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400">
              <Building2 className="h-4 w-4" />
              {t('medsupplier.workspace.activeOrganization')}
            </div>
            <p className="font-semibold text-slate-950 dark:text-white">{currentOrganization?.name || t('medsupplier.workspace.noOrganization')}</p>
          </div>
        </div>
      </div>

      <CrudErrorBanner message={error} onClose={() => setError('')} />

      {section.key === 'integration' ? (
        <ProductModePanel
          status={integrationStatus}
          loading={integrationLoading}
          onRefresh={loadIntegrationStatus}
          t={t}
        />
      ) : section.key === 'cockpit' ? (
        <PrivateCockpitPanel
          data={cockpitData}
          loading={cockpitLoading}
          onRefresh={loadPrivateCockpit}
          t={t}
          formatValue={formatValue}
        />
      ) : (
        <section className="rounded-lg border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="flex items-center justify-between border-b border-slate-200 px-5 py-4 dark:border-slate-800">
            <div>
              <h2 className="text-lg font-semibold text-slate-950 dark:text-white">{t('medsupplier.workspace.records')}</h2>
              <p className="text-sm text-slate-500 dark:text-slate-400">{t('medsupplier.workspace.recordsInScope', { count })}</p>
            </div>
            <button
              type="button"
              onClick={loadData}
              className="inline-flex items-center gap-2 rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
            >
              <RefreshCw className="h-4 w-4" />
              {t('medsupplier.workspace.refresh')}
            </button>
          </div>

          {loading ? (
            <div className="flex justify-center p-8">
              <div className="h-10 w-10 animate-spin rounded-full border-b-2 border-blue-500" />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-slate-100 dark:bg-slate-800/60">
                  <tr>
                    {section.columns.map(([field, label]) => (
                      <th key={label} className="px-5 py-3 text-left text-xs font-medium uppercase text-slate-600 dark:text-slate-300">
                        {translateColumnLabel(field, label)}
                      </th>
                    ))}
                    {canMutate ? (
                      <th className="px-5 py-3 text-right text-xs font-medium uppercase text-slate-600 dark:text-slate-300">
                        {t('medsupplier.workspace.actions')}
                      </th>
                    ) : null}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
                  {items.map((item) => (
                    <tr key={item.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/60">
                      {section.columns.map(([field]) => (
                        <td key={field} className="px-5 py-4 text-sm text-slate-700 dark:text-slate-200">
                          {formatValue(item[field])}
                        </td>
                      ))}
                      {canMutate ? (
                        <td className="px-5 py-4">
                          <div className="flex justify-end gap-2">
                            {(section.workflowActions || []).map((workflowAction) => {
                              const disabledReason = getWorkflowDisabledReason(workflowAction, item, t);
                              const workflowLabel = translateWorkflowAction(workflowAction);
                              return (
                                <button
                                  key={workflowAction.action}
                                  type="button"
                                  disabled={Boolean(disabledReason)}
                                  onClick={() => handleWorkflowAction(item, workflowAction)}
                                  className="inline-flex h-9 items-center justify-center rounded-lg border border-blue-200 px-2 text-xs font-medium text-blue-700 transition hover:bg-blue-50 disabled:cursor-not-allowed disabled:border-slate-200 disabled:text-slate-400 disabled:hover:bg-transparent dark:border-blue-900 dark:text-blue-200 dark:hover:bg-blue-950/40 dark:disabled:border-slate-800 dark:disabled:text-slate-500"
                                  title={disabledReason || workflowLabel}
                                >
                                  {workflowLabel}
                                </button>
                              );
                            })}
                            <button
                              type="button"
                              onClick={() => openEditForm(item)}
                              className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-slate-300 text-slate-600 transition hover:bg-slate-100 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
                              aria-label={t('medsupplier.workspace.editAria', { section: sectionLabel })}
                              title={t('common.buttons.edit')}
                            >
                              <Pencil className="h-4 w-4" />
                            </button>
                            <button
                              type="button"
                              onClick={() => handleDelete(item)}
                              className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-red-200 text-red-600 transition hover:bg-red-50 dark:border-red-900 dark:text-red-300 dark:hover:bg-red-950/40"
                              aria-label={t('medsupplier.workspace.deleteAria', { section: sectionLabel })}
                              title={t('common.buttons.delete')}
                            >
                              <Trash2 className="h-4 w-4" />
                            </button>
                          </div>
                        </td>
                      ) : null}
                    </tr>
                  ))}
                  {items.length === 0 && (
                    <CrudEmptyState
                      colSpan={(section.columns.length || 1) + (canMutate ? 1 : 0)}
                      message={canMutate ? t('medsupplier.workspace.noRecordsCreate') : t('medsupplier.workspace.noRecords')}
                    />
                  )}
                </tbody>
              </table>
            </div>
          )}
        </section>
      )}

      <section className="grid grid-cols-1 gap-3 md:grid-cols-4">
        {relatedSections.map((item) => {
          const RelatedIcon = item.icon;
          return (
            <Link
              key={item.key}
              to={`/medsupplier/${item.key}`}
              className="rounded-lg border border-slate-200 bg-white p-4 text-sm shadow-sm transition hover:border-blue-300 hover:bg-blue-50 dark:border-slate-800 dark:bg-slate-900 dark:hover:border-blue-800 dark:hover:bg-blue-950/30"
            >
              <RelatedIcon className="mb-2 h-5 w-5 text-blue-700 dark:text-blue-200" />
              <p className="font-semibold text-slate-950 dark:text-white">{translateSectionLabel(item)}</p>
              <p className="mt-1 line-clamp-2 text-slate-500 dark:text-slate-400">{translateSectionDescription(item)}</p>
            </Link>
          );
        })}
      </section>

      <Modal
        title={editingRecord ? t('medsupplier.workspace.editTitle', { section: sectionLabel }) : t('medsupplier.workspace.newTitle', { section: sectionLabel })}
        isOpen={isFormOpen}
        onClose={closeForm}
        maxWidth="max-w-3xl"
      >
        <RecordForm
          fields={permittedFields}
          form={form}
          lookupOptions={lookupOptions}
          onChange={updateFormValue}
          onSubmit={handleSubmit}
          onCancel={closeForm}
          saving={saving}
          submitLabel={editingRecord ? t('medsupplier.workspace.saveChanges') : t('medsupplier.workspace.createRecord')}
          t={t}
          translateFieldLabel={translateFieldLabel}
          translateOptionLabel={translateOptionLabel}
        />
      </Modal>
    </div>
  );
};

export default MedSupplierWorkspace;
