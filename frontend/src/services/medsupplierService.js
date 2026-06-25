import api from './api';

const normalizeList = (data) => Array.isArray(data) ? data : data?.results || [];

const medsupplierService = {
  getSummary: async (organizationId) => {
    const response = await api.get('/medsupplier/dashboard/summary/', {
      params: { organization_id: organizationId },
    });
    return response.data;
  },

  getAccounts: async (organizationId, params = {}) => {
    const response = await api.get('/medsupplier/accounts/', {
      params: { ...params, organization_id: organizationId },
    });
    return normalizeList(response.data);
  },

  getIntegrationStatus: async (organizationId) => {
    const response = await api.get('/medsupplier/integration/status/', {
      params: { organization_id: organizationId },
    });
    return response.data;
  },

  list: async (resource, organizationId, params = {}) => {
    const response = await api.get(`/medsupplier/${resource}/`, {
      params: { ...params, organization_id: organizationId },
    });
    return {
      items: normalizeList(response.data),
      count: response.data?.count ?? normalizeList(response.data).length,
    };
  },
};

export default medsupplierService;
