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
import medsupplierService from '../../../services/medsupplierService';
import { medsupplierSections } from '../medsupplierSections';

const StatTile = ({ icon: Icon, label, value, tone = 'blue' }) => {
  const tones = {
    blue: 'bg-blue-50 text-blue-700 dark:bg-blue-950/40 dark:text-blue-200',
    emerald: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-200',
    amber: 'bg-amber-50 text-amber-700 dark:bg-amber-950/40 dark:text-amber-200',
    rose: 'bg-rose-50 text-rose-700 dark:bg-rose-950/40 dark:text-rose-200',
    slate: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-200',
  };

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
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
  <div className={`rounded-lg border px-3 py-2 text-sm ${
    active
      ? 'border-blue-300 bg-blue-50 text-blue-800 dark:border-blue-800 dark:bg-blue-950/40 dark:text-blue-200'
      : 'border-slate-200 bg-white text-slate-600 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-300'
  }`}>
    {label}
  </div>
);

const MedSupplierDashboard = () => {
  const { currentOrganization } = useAuth();
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
      setError('No se pudo cargar ISO Smart MedSupplier.');
    } finally {
      setLoading(false);
    }
  }, [organizationId]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const flow = useMemo(() => ([
    'Cuenta/cliente',
    'Reuniones',
    'Requisitos',
    'Documentos',
    'RFQ/cotización',
    'PO',
    'Lote',
    'Shipment',
    'Inspección',
    'NCR/CAPA',
    'Scorecard/QBR',
  ]), []);

  const visibleSections = useMemo(() => (
    medsupplierSections.filter((section) => (
      !section.requiresPermission || permissions?.permissions?.[section.requiresPermission]
    ))
  ), [permissions]);

  if (loading) {
    return (
      <div className="flex justify-center p-8">
        <div className="h-12 w-12 animate-spin rounded-full border-b-2 border-blue-500" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <CrudPageHeader
        title="ISO Smart MedSupplier"
        subtitle={`Torre de control regulada Supplier-Customer. Vista activa: ${permissions?.side || summary?.side || 'scope'} / ${permissions?.role || summary?.role || 'rol pendiente'}.`}
      />

      <CrudErrorBanner message={error} onClose={() => setError('')} />

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatTile icon={Users} label="Cuentas activas" value={summary?.active_accounts ?? 0} tone="blue" />
        <StatTile icon={ClipboardCheck} label="Acciones abiertas" value={summary?.open_actions ?? 0} tone="amber" />
        <StatTile icon={AlertTriangle} label="Eventos de calidad" value={summary?.open_quality_events ?? 0} tone="rose" />
        <StatTile icon={Gauge} label="Scorecard promedio" value={Number(summary?.average_scorecard || 0).toFixed(1)} tone="emerald" />
      </div>

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
        <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900 xl:col-span-2">
          <div className="mb-4 flex items-center gap-2">
            <ShieldCheck className="h-5 w-5 text-blue-600 dark:text-blue-300" />
            <h2 className="text-lg font-semibold text-slate-950 dark:text-white">Flujo regulado Supplier-Customer</h2>
          </div>
          <div className="grid grid-cols-2 gap-2 md:grid-cols-4 xl:grid-cols-6">
            {flow.map((step, index) => (
              <FlowStep key={step} label={step} active={index <= 4} />
            ))}
          </div>
        </section>

        <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="mb-4 flex items-center gap-2">
            <FileText className="h-5 w-5 text-blue-600 dark:text-blue-300" />
            <h2 className="text-lg font-semibold text-slate-950 dark:text-white">Visibilidad</h2>
          </div>
          <div className="space-y-3">
            <div className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2 dark:bg-slate-800">
              <span className="text-sm text-slate-600 dark:text-slate-300">Registros compartidos</span>
              <span className="font-semibold text-slate-950 dark:text-white">{summary?.shared_records ?? 0}</span>
            </div>
            <div className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2 dark:bg-slate-800">
              <span className="text-sm text-slate-600 dark:text-slate-300">Registros privados</span>
              <span className="font-semibold text-slate-950 dark:text-white">{summary?.private_records ?? 0}</span>
            </div>
            <div className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2 dark:bg-slate-800">
              <span className="text-sm text-slate-600 dark:text-slate-300">RFQ/cotizaciones</span>
              <span className="font-semibold text-slate-950 dark:text-white">{summary?.rfqs ?? 0}</span>
            </div>
          </div>
        </section>
      </div>

      <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div className="mb-4 flex items-center gap-2">
          <ShieldCheck className="h-5 w-5 text-blue-600 dark:text-blue-300" />
          <h2 className="text-lg font-semibold text-slate-950 dark:text-white">Workspace MedSupplier</h2>
        </div>
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-4">
          {visibleSections.filter((section) => section.key !== 'accounts').slice(0, 12).map((section) => {
            const SectionIcon = section.icon;
            return (
              <Link
                key={section.key}
                to={`/medsupplier/${section.key}`}
                className="rounded-lg border border-slate-200 p-4 transition hover:border-blue-300 hover:bg-blue-50 dark:border-slate-800 dark:hover:border-blue-800 dark:hover:bg-blue-950/30"
              >
                <SectionIcon className="mb-2 h-5 w-5 text-blue-700 dark:text-blue-200" />
                <p className="font-semibold text-slate-950 dark:text-white">{section.label}</p>
                <p className="mt-1 line-clamp-2 text-sm text-slate-500 dark:text-slate-400">{section.description}</p>
              </Link>
            );
          })}
        </div>
      </section>

      <section className="rounded-lg border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div className="flex items-center justify-between border-b border-slate-200 px-5 py-4 dark:border-slate-800">
          <div className="flex items-center gap-2">
            <PackageCheck className="h-5 w-5 text-blue-600 dark:text-blue-300" />
            <h2 className="text-lg font-semibold text-slate-950 dark:text-white">Cliente 360 básico</h2>
          </div>
          <div className="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400">
            <Truck className="h-4 w-4" />
            {summary?.shipments_in_transit ?? 0} shipments en tránsito
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-100 dark:bg-slate-800/60">
              <tr>
                <th className="px-5 py-3 text-left text-xs font-medium uppercase text-slate-600 dark:text-slate-300">Cuenta</th>
                <th className="px-5 py-3 text-left text-xs font-medium uppercase text-slate-600 dark:text-slate-300">Código</th>
                <th className="px-5 py-3 text-left text-xs font-medium uppercase text-slate-600 dark:text-slate-300">Estado</th>
                <th className="px-5 py-3 text-left text-xs font-medium uppercase text-slate-600 dark:text-slate-300">Riesgo</th>
                <th className="px-5 py-3 text-left text-xs font-medium uppercase text-slate-600 dark:text-slate-300">Visibilidad</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
              {accounts.map((account) => (
                <tr key={account.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/60">
                  <td className="px-5 py-4 text-sm font-medium text-slate-950 dark:text-white">{account.name}</td>
                  <td className="px-5 py-4 text-sm text-slate-600 dark:text-slate-300">{account.account_code}</td>
                  <td className="px-5 py-4 text-sm text-slate-600 dark:text-slate-300">{account.status}</td>
                  <td className="px-5 py-4 text-sm text-slate-600 dark:text-slate-300">{account.risk_level}</td>
                  <td className="px-5 py-4 text-sm text-slate-600 dark:text-slate-300">{account.visibility}</td>
                </tr>
              ))}
              {accounts.length === 0 && <CrudEmptyState colSpan={5} message="No hay cuentas Supplier-Customer registradas." />}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
};

export default MedSupplierDashboard;
