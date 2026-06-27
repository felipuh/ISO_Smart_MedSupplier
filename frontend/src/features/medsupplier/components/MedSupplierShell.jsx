import React, { useEffect, useState } from 'react';
import { Link, NavLink, Outlet } from 'react-router-dom';
import { LogOut, Moon, Sun } from 'lucide-react';
import { medsupplierSections } from '../medsupplierSections';
import { useAuth } from '../../../context/AuthContext';
import { useTheme } from '../../../context/ThemeContext';
import medsupplierService from '../../../services/medsupplierService';

const hasSectionAccess = (section, permissions) => {
  if (!section.requiresPermission) return true;
  return Boolean(permissions?.permissions?.[section.requiresPermission]);
};

const MedSupplierShell = () => {
  const { currentOrganization, logout, user } = useAuth();
  const { isDark, toggleTheme } = useTheme();
  const [permissions, setPermissions] = useState(null);
  const organizationId = currentOrganization?.id;

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

  const visibleSections = medsupplierSections.filter((item) => hasSectionAccess(item, permissions));

  return (
    <div className="min-h-screen bg-slate-50 text-slate-950 dark:bg-slate-950 dark:text-white">
      <aside className="fixed inset-y-0 left-0 z-40 flex w-72 flex-col border-r border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900">
        <div className="border-b border-slate-200 p-5 dark:border-slate-800">
          <Link to="/" className="block">
            <p className="text-xl font-bold tracking-normal">ISO Smart MedSupplier</p>
            <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">Torre Supplier-Customer regulada</p>
          </Link>
        </div>

        <nav className="flex-1 space-y-1 overflow-y-auto p-3">
          {visibleSections.map((item) => {
            const Icon = item.icon;
            const to = item.key === 'accounts' ? '/medsupplier/accounts' : `/medsupplier/${item.key}`;
            return (
              <NavLink
                key={item.key}
                to={to}
                className={({ isActive }) => `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition ${
                  isActive
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'text-slate-600 hover:bg-slate-100 hover:text-slate-950 dark:text-slate-300 dark:hover:bg-slate-800 dark:hover:text-white'
                }`}
              >
                <Icon className="h-4 w-4" />
                {item.label}
              </NavLink>
            );
          })}
        </nav>

        <div className="border-t border-slate-200 p-4 dark:border-slate-800">
          <p className="truncate text-sm font-semibold">{currentOrganization?.name || 'Sin organización'}</p>
          <p className="truncate text-xs text-slate-500 dark:text-slate-400">{user?.email}</p>
          <p className="mt-1 truncate text-xs text-slate-500 dark:text-slate-400">{permissions?.role || 'Permisos MedSupplier'}</p>
        </div>
      </aside>

      <div className="pl-72">
        <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/95 px-6 py-3 backdrop-blur dark:border-slate-800 dark:bg-slate-900/95">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="text-sm font-medium text-blue-700 dark:text-blue-200">Producto vendible por separado, gobernado por AdminApps</p>
              <p className="text-xs text-slate-500 dark:text-slate-400">AdminApps controla clientes, usuarios, roles, licencias y habilitación MEDSUPPLIER.</p>
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={toggleTheme}
                className="rounded-lg border border-slate-300 p-2 text-slate-600 hover:bg-slate-100 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
                aria-label={isDark ? 'Cambiar a tema claro' : 'Cambiar a tema oscuro'}
                title={isDark ? 'Cambiar a tema claro' : 'Cambiar a tema oscuro'}
              >
                {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
              </button>
              <button
                type="button"
                onClick={logout}
                className="flex items-center gap-2 rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
              >
                <LogOut className="h-4 w-4" />
                Salir
              </button>
            </div>
          </div>
        </header>

        <main className="p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default MedSupplierShell;
