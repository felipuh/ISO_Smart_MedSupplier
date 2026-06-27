import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { Building2, KeyRound, LockKeyhole, Pencil, Plus, RefreshCw, ShieldCheck, Trash2 } from 'lucide-react';
import CrudEmptyState from '../../../components/Common/CrudEmptyState';
import CrudErrorBanner from '../../../components/Common/CrudErrorBanner';
import Modal from '../../../components/Common/Modal';
import { useAuth } from '../../../context/AuthContext';
import medsupplierService from '../../../services/medsupplierService';
import { getMedSupplierSection, medsupplierSections } from '../medsupplierSections';

const formatCell = (value) => {
  if (value === null || value === undefined || value === '') return '—';
  if (typeof value === 'number') return value.toLocaleString();
  if (typeof value === 'boolean') return value ? 'Sí' : 'No';
  if (typeof value === 'string' && value.includes('T') && value.endsWith('Z')) {
    return new Date(value).toLocaleString();
  }
  return String(value);
};

const statusLabel = (value) => (value ? 'Activo' : 'Requiere atención');

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

const getWorkflowDisabledReason = (workflowAction, item) => {
  const statusReason = workflowAction.disabledStatuses?.[item.status];
  if (statusReason) return statusReason;

  if (workflowAction.disableWhenExpired && item.valid_until) {
    const validUntil = new Date(`${item.valid_until}T00:00:00`);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    if (validUntil < today) {
      return workflowAction.expiredReason || 'Registro expirado.';
    }
  }

  if (workflowAction.requiredField && !String(item[workflowAction.requiredField] || '').trim()) {
    return workflowAction.requiredFieldReason || 'Falta información requerida.';
  }

  return '';
};

const RecordForm = ({ fields, form, lookupOptions, onChange, onSubmit, onCancel, saving, submitLabel }) => (
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
              {field.label}
            </label>
          );
        }

        return (
          <label key={field.name} className="form-label-muted">
            {field.label}
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
                    {field.type === 'relation' ? <option value="">Selecciona una opción</option> : null}
                    {(lookupOptions[field.name] || []).map((item) => (
                      <option key={item.id} value={item.id}>
                        {formatRelationLabel(item, field.optionFields)}
                      </option>
                    ))}
                  </>
                ) : (
                  (field.options || []).map(([value, label]) => (
                    <option key={value} value={value}>{label}</option>
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
        Cancelar
      </button>
      <button type="submit" className="btn-primary" disabled={saving}>
        {saving ? 'Guardando...' : submitLabel}
      </button>
    </div>
  </form>
);

const ProductModePanel = ({ status, loading, onRefresh }) => (
  <div className="space-y-4">
    <section className="rounded-lg border border-blue-200 bg-blue-50 p-5 dark:border-blue-900 dark:bg-blue-950/30">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="mb-2 flex items-center gap-2 text-blue-800 dark:text-blue-200">
            <ShieldCheck className="h-5 w-5" />
            <h2 className="text-lg font-semibold">AdminApps es la fuente de verdad</h2>
          </div>
          <p className="max-w-4xl text-sm text-blue-950 dark:text-blue-100">
            Las organizaciones, usuarios, roles, licencias y habilitación del módulo MEDSUPPLIER se crean y gobiernan desde AdminApps. MedSupplier puede venderse por separado o junto a Iso Smart, pero no administra identidades ni clientes por fuera del cerebro comercial.
          </p>
        </div>
        <button
          type="button"
          onClick={onRefresh}
          className="flex items-center gap-2 rounded-lg border border-blue-300 px-3 py-2 text-sm font-medium text-blue-800 hover:bg-blue-100 dark:border-blue-800 dark:text-blue-100 dark:hover:bg-blue-900/40"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          Actualizar
        </button>
      </div>
    </section>

    <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
      <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div className="mb-3 flex items-center gap-2 text-emerald-700 dark:text-emerald-200">
          <KeyRound className="h-5 w-5" />
          <h3 className="font-semibold">Identidad centralizada</h3>
        </div>
        <p className="text-sm text-slate-600 dark:text-slate-300">
          Estado AdminApps: <strong>{statusLabel(status?.adminapps?.available)}</strong>
        </p>
        <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">
          Usuarios, roles y organización activa se sincronizan desde AdminApps.
        </p>
      </div>
      <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div className="mb-3 flex items-center gap-2 text-blue-700 dark:text-blue-200">
          <Building2 className="h-5 w-5" />
          <h3 className="font-semibold">Habilitación MEDSUPPLIER</h3>
        </div>
        <p className="text-sm text-slate-600 dark:text-slate-300">
          Módulo: <strong>{statusLabel(status?.entitlement?.enabled)}</strong>
        </p>
        <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">
          Código comercial: <strong>{status?.module_code || 'MEDSUPPLIER'}</strong>
        </p>
      </div>
      <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div className="mb-3 flex items-center gap-2 text-amber-700 dark:text-amber-200">
          <LockKeyhole className="h-5 w-5" />
          <h3 className="font-semibold">Separación comercial</h3>
        </div>
        <p className="text-sm text-slate-600 dark:text-slate-300">
          Modo: <strong>{status?.product_mode || 'integrated'}</strong>
        </p>
        <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">
          La visibilidad <strong>private</strong> protege pipeline, margen, forecast y notas internas del proveedor.
        </p>
      </div>
    </div>
  </div>
);

const MedSupplierWorkspace = () => {
  const { sectionKey = 'accounts' } = useParams();
  const section = getMedSupplierSection(sectionKey);
  const { currentOrganization } = useAuth();
  const organizationId = currentOrganization?.id;
  const [items, setItems] = useState([]);
  const [count, setCount] = useState(0);
  const [loading, setLoading] = useState(Boolean(section.resource));
  const [integrationStatus, setIntegrationStatus] = useState(null);
  const [integrationLoading, setIntegrationLoading] = useState(false);
  const [error, setError] = useState('');
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingRecord, setEditingRecord] = useState(null);
  const [form, setForm] = useState(() => buildInitialForm(section.formFields || []));
  const [saving, setSaving] = useState(false);
  const [lookupOptions, setLookupOptions] = useState({});
  const canMutate = Boolean(section.resource && section.formFields?.length);

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
      setError(`No se pudo cargar ${section.label}.`);
    } finally {
      setLoading(false);
    }
  }, [organizationId, section.resource, section.label]);

  const loadIntegrationStatus = useCallback(async () => {
    if (!organizationId || section.key !== 'integration') return;

    try {
      setIntegrationLoading(true);
      setError('');
      const result = await medsupplierService.getIntegrationStatus(organizationId);
      setIntegrationStatus(result);
    } catch (err) {
      console.error('Error loading MedSupplier integration status:', err);
      setError('No se pudo cargar el estado de integración con AdminApps.');
    } finally {
      setIntegrationLoading(false);
    }
  }, [organizationId, section.key]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  useEffect(() => {
    loadIntegrationStatus();
  }, [loadIntegrationStatus]);

  useEffect(() => {
    const relationFields = (section.formFields || []).filter((field) => ['relation', 'multirelation'].includes(field.type));
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
          setError(extractApiError(err, 'No se pudieron cargar los datos relacionados.'));
        }
      }
    };

    loadLookups();
    return () => {
      mounted = false;
    };
  }, [organizationId, section.formFields]);

  useEffect(() => {
    setIsFormOpen(false);
    setEditingRecord(null);
    setForm(buildInitialForm(section.formFields || []));
  }, [section.key, section.formFields]);

  const relatedSections = useMemo(() => (
    medsupplierSections.filter((item) => item.key !== section.key).slice(0, 4)
  ), [section.key]);

  const Icon = section.icon;

  const openCreateForm = () => {
    setEditingRecord(null);
    setForm(buildInitialForm(section.formFields || []));
    setIsFormOpen(true);
  };

  const openEditForm = (record) => {
    setEditingRecord(record);
    setForm(buildInitialForm(section.formFields || [], record));
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
    if (!organizationId || !section.resource || !section.formFields?.length) return;

    try {
      setSaving(true);
      setError('');
      const payload = normalizePayload(section.formFields, form);
      if (editingRecord) {
        await medsupplierService.update(section.resource, organizationId, editingRecord.id, payload);
      } else {
        await medsupplierService.create(section.resource, organizationId, payload);
      }
      setIsFormOpen(false);
      setEditingRecord(null);
      await loadData();
    } catch (err) {
      setError(extractApiError(err, `No se pudo guardar ${section.label}.`));
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (record) => {
    if (!organizationId || !section.resource) return;
    const label = record.name || record.account_code || record.id;
    const confirmed = window.confirm(`¿Eliminar "${label}"? Esta acción no se puede deshacer.`);
    if (!confirmed) return;

    try {
      setSaving(true);
      setError('');
      await medsupplierService.remove(section.resource, organizationId, record.id);
      await loadData();
    } catch (err) {
      setError(extractApiError(err, `No se pudo eliminar ${section.label}.`));
    } finally {
      setSaving(false);
    }
  };

  const handleWorkflowAction = async (record, workflowAction) => {
    if (!organizationId || !section.resource) return;
    const confirmed = window.confirm(workflowAction.confirm || `¿Ejecutar ${workflowAction.label}?`);
    if (!confirmed) return;

    try {
      setSaving(true);
      setError('');
      await medsupplierService.runWorkflowAction(section.resource, organizationId, record.id, workflowAction.action);
      await loadData();
    } catch (err) {
      setError(extractApiError(err, `No se pudo ejecutar ${workflowAction.label}.`));
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
            ISO Smart MedSupplier
          </div>
          <h1 className="text-3xl font-bold text-slate-950 dark:text-white">{section.label}</h1>
          <p className="mt-1 max-w-3xl text-slate-600 dark:text-slate-300">{section.description}</p>
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
              Nuevo
            </button>
          ) : null}
          <div className="rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm shadow-sm dark:border-slate-800 dark:bg-slate-900">
            <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400">
              <Building2 className="h-4 w-4" />
              Organización activa
            </div>
            <p className="font-semibold text-slate-950 dark:text-white">{currentOrganization?.name || 'Sin organización'}</p>
          </div>
        </div>
      </div>

      <CrudErrorBanner message={error} onClose={() => setError('')} />

      {section.key === 'integration' ? (
        <ProductModePanel
          status={integrationStatus}
          loading={integrationLoading}
          onRefresh={loadIntegrationStatus}
        />
      ) : (
        <section className="rounded-lg border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="flex items-center justify-between border-b border-slate-200 px-5 py-4 dark:border-slate-800">
            <div>
              <h2 className="text-lg font-semibold text-slate-950 dark:text-white">Registros</h2>
              <p className="text-sm text-slate-500 dark:text-slate-400">{count} registros en el scope activo</p>
            </div>
            <button
              type="button"
              onClick={loadData}
              className="inline-flex items-center gap-2 rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
            >
              <RefreshCw className="h-4 w-4" />
              Actualizar
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
                    {section.columns.map(([, label]) => (
                      <th key={label} className="px-5 py-3 text-left text-xs font-medium uppercase text-slate-600 dark:text-slate-300">
                        {label}
                      </th>
                    ))}
                    {canMutate ? (
                      <th className="px-5 py-3 text-right text-xs font-medium uppercase text-slate-600 dark:text-slate-300">
                        Acciones
                      </th>
                    ) : null}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
                  {items.map((item) => (
                    <tr key={item.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/60">
                      {section.columns.map(([field]) => (
                        <td key={field} className="px-5 py-4 text-sm text-slate-700 dark:text-slate-200">
                          {formatCell(item[field])}
                        </td>
                      ))}
                      {canMutate ? (
                        <td className="px-5 py-4">
                          <div className="flex justify-end gap-2">
                            {(section.workflowActions || []).map((workflowAction) => {
                              const disabledReason = getWorkflowDisabledReason(workflowAction, item);
                              return (
                                <button
                                  key={workflowAction.action}
                                  type="button"
                                  disabled={Boolean(disabledReason)}
                                  onClick={() => handleWorkflowAction(item, workflowAction)}
                                  className="inline-flex h-9 items-center justify-center rounded-lg border border-blue-200 px-2 text-xs font-medium text-blue-700 transition hover:bg-blue-50 disabled:cursor-not-allowed disabled:border-slate-200 disabled:text-slate-400 disabled:hover:bg-transparent dark:border-blue-900 dark:text-blue-200 dark:hover:bg-blue-950/40 dark:disabled:border-slate-800 dark:disabled:text-slate-500"
                                  title={disabledReason || workflowAction.label}
                                >
                                  {workflowAction.label}
                                </button>
                              );
                            })}
                            <button
                              type="button"
                              onClick={() => openEditForm(item)}
                              className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-slate-300 text-slate-600 transition hover:bg-slate-100 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
                              aria-label={`Editar ${section.label}`}
                              title="Editar"
                            >
                              <Pencil className="h-4 w-4" />
                            </button>
                            <button
                              type="button"
                              onClick={() => handleDelete(item)}
                              className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-red-200 text-red-600 transition hover:bg-red-50 dark:border-red-900 dark:text-red-300 dark:hover:bg-red-950/40"
                              aria-label={`Eliminar ${section.label}`}
                              title="Eliminar"
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
                      message={canMutate ? 'No hay registros todavía. Crea el primero para iniciar el workspace.' : 'No hay registros todavía.'}
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
              <p className="font-semibold text-slate-950 dark:text-white">{item.label}</p>
              <p className="mt-1 line-clamp-2 text-slate-500 dark:text-slate-400">{item.description}</p>
            </Link>
          );
        })}
      </section>

      <Modal
        title={editingRecord ? `Editar ${section.label}` : `Nuevo ${section.label}`}
        isOpen={isFormOpen}
        onClose={closeForm}
        maxWidth="max-w-3xl"
      >
        <RecordForm
          fields={section.formFields || []}
          form={form}
          lookupOptions={lookupOptions}
          onChange={updateFormValue}
          onSubmit={handleSubmit}
          onCancel={closeForm}
          saving={saving}
          submitLabel={editingRecord ? 'Guardar cambios' : 'Crear registro'}
        />
      </Modal>
    </div>
  );
};

export default MedSupplierWorkspace;
