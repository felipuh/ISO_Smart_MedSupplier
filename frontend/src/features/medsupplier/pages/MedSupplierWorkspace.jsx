import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { Building2, KeyRound, LockKeyhole, RefreshCw, ShieldCheck } from 'lucide-react';
import CrudEmptyState from '../../../components/Common/CrudEmptyState';
import CrudErrorBanner from '../../../components/Common/CrudErrorBanner';
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

  const relatedSections = useMemo(() => (
    medsupplierSections.filter((item) => item.key !== section.key).slice(0, 4)
  ), [section.key]);

  const Icon = section.icon;

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
        <div className="rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400">
            <Building2 className="h-4 w-4" />
            Organización activa
          </div>
          <p className="font-semibold text-slate-950 dark:text-white">{currentOrganization?.name || 'Sin organización'}</p>
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
              className="rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
            >
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
                    </tr>
                  ))}
                  {items.length === 0 && <CrudEmptyState colSpan={section.columns.length || 1} message="No hay registros todavía." />}
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
    </div>
  );
};

export default MedSupplierWorkspace;
