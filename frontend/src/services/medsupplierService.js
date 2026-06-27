import api from './api';

const normalizeList = (data) => Array.isArray(data) ? data : data?.results || [];

const buildRequestPayload = (payload) => {
  const entries = Object.entries(payload || {});
  const hasFile = entries.some(([, value]) => value instanceof File);
  if (!hasFile) return { data: payload };

  const formData = new FormData();
  entries.forEach(([key, value]) => {
    if (Array.isArray(value)) {
      value.forEach((item) => formData.append(key, item));
      return;
    }
    if (value !== undefined) {
      formData.append(key, value);
    }
  });
  return { data: formData };
};

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

  create: async (resource, organizationId, payload) => {
    const request = buildRequestPayload(payload);
    const response = await api.post(`/medsupplier/${resource}/`, request.data, {
      params: { organization_id: organizationId },
    });
    return response.data;
  },

  update: async (resource, organizationId, id, payload) => {
    const request = buildRequestPayload(payload);
    const response = await api.patch(`/medsupplier/${resource}/${id}/`, request.data, {
      params: { organization_id: organizationId },
    });
    return response.data;
  },

  remove: async (resource, organizationId, id) => {
    await api.delete(`/medsupplier/${resource}/${id}/`, {
      params: { organization_id: organizationId },
    });
  },

  runWorkflowAction: async (resource, organizationId, id, action, payload = {}) => {
    const response = await api.post(`/medsupplier/${resource}/${id}/${action}/`, payload, {
      params: { organization_id: organizationId },
    });
    return response.data;
  },
};

export default medsupplierService;
