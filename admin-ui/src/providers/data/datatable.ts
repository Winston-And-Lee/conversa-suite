import { DataProvider } from '@refinedev/core';
import { axiosInstance, generateFilter, generateSort } from '@refinedev/simple-rest';
import { AxiosInstance } from 'axios';
import queryString from 'query-string';

import { request } from '@/api-requests';

type MethodTypes = 'get' | 'delete' | 'head' | 'options';
type MethodTypesWithBody = 'post' | 'put' | 'patch';

export interface GetOneResponse {
  data: any;
  schema?: any;
}

export const datatableProvider = (
  apiUrl: string,
  httpClient: AxiosInstance = axiosInstance
): Omit<Required<DataProvider>, 'createMany' | 'updateMany' | 'deleteMany'> => ({
  getList: async ({ resource, pagination, filters, sorters, meta }) => {
    const url = `${apiUrl}/${resource}/data`;

    const { current = 1, pageSize = 10, mode = 'server' } = pagination ?? {};

    const { headers: headersFromMeta, method } = meta ?? {};
    const requestMethod = (method as MethodTypes) ?? 'get';

    const queryFilters = generateFilter(filters);

    const query: {
      _page?: number;
      _pageSize?: number;
      _sort?: string;
      _order?: string;
    } = {};

    if (mode === 'server') {
      query._page = current;
      query._pageSize = pageSize;
    }

    const generatedSort = generateSort(sorters);
    if (generatedSort) {
      const { _sort, _order } = generatedSort;
      query._sort = _sort.join(',');
      query._order = _order.join(',');
    }

    const { data, status, headers } = await request({
      method: requestMethod,
      url: `${url}?${queryString.stringify(query)}&${queryString.stringify(queryFilters)}`,
      headers: headersFromMeta
    });

    const schema = {
      'main': {
        fields: data['columns']
      },
      'datatable': data['columns']
    };

    data['data']['__schema'] = schema;

    return {
      data: data['data'],
      total: data['totalData'] || data.length,
      schema: schema
    };
  },

  getMany: async ({ resource, ids, meta }) => {
    const { headers: headersFromMeta, method } = meta ?? {};
    const requestMethod = (method as MethodTypes) ?? 'get';

    const { data, status, headers } = await request({
      method: requestMethod,
      url: `${apiUrl}/${resource}?${queryString.stringify({ id: ids })}`,
      headers: headersFromMeta
    });

    return {
      data
    };
  },

  create: async ({ resource, variables, meta }) => {
    const url = `${apiUrl}/${resource}/data`;

    const { headers: headersFromMeta, method } = meta ?? {};
    const requestMethod = (method as MethodTypesWithBody) ?? 'post';

    const { data, status, headers } = await request({
      method: requestMethod,
      url: url,
      body: variables,
      headers: headersFromMeta
    });

    return {
      data
    };
  },

  update: async ({ resource, id, variables, meta }) => {
    const url = `${apiUrl}/${resource}/data/${id}`;

    const { headers: headersFromMeta, method } = meta ?? {};
    const requestMethod = (method as MethodTypesWithBody) ?? 'patch';

    const { data, status, headers } = await request({
      method: requestMethod,
      url: url,
      body: variables,
      headers: headersFromMeta
    });

    return {
      data: data
    };
  },

  getOne: async ({ resource, id, meta }) => {
    const url = `${apiUrl}/${resource}/data/${id}`;

    const { headers: headersFromMeta, method } = meta ?? {};
    const requestMethod = (method as MethodTypes) ?? 'get';

    const { data, status, headers } = await request({
      method: requestMethod,
      url: url,
      headers: headersFromMeta
    });


    const schema = {
      'main': {
        fields: data['columns']
      },
      'datatable': data['columns']
    };

    if (data['data_schema']) {
      data['data']['__schema'] = schema;
    }

    return {
      data: data['data'],
      schema: schema
    };
  },

  deleteOne: async ({ resource, id, variables, meta }) => {
    const url = `${apiUrl}/${resource}/data/${id}`;

    const { headers: headersFromMeta, method } = meta ?? {};
    const requestMethod = (method as MethodTypesWithBody) ?? 'delete';

    const { data, status, headers } = await request({
      method: requestMethod,
      url: url,
      body: variables,
      headers: headersFromMeta
    });

    return {
      data
    };
  },

  getApiUrl: () => {
    return apiUrl;
  },

  custom: async ({ url, method, filters, sorters, payload, query, headers }) => {
    let requestUrl = `${url}?`;

    if (sorters) {
      const generatedSort = generateSort(sorters);
      if (generatedSort) {
        const { _sort, _order } = generatedSort;
        const sortQuery = {
          _sort: _sort.join(','),
          _order: _order.join(',')
        };
        requestUrl = `${requestUrl}&${queryString.stringify(sortQuery)}`;
      }
    }

    if (filters) {
      const filterQuery = generateFilter(filters);
      requestUrl = `${requestUrl}&${queryString.stringify(filterQuery)}`;
    }

    if (query) {
      requestUrl = `${requestUrl}&${queryString.stringify(query)}`;
    }

    let responseData;
    switch (method) {
      case 'put':
      case 'post':
      case 'patch':
        responseData = await request({
          method: method,
          url: url,
          body: payload,
          headers: headers
        });
        break;
      case 'delete':
        responseData = await request({
          method: method,
          url: url,
          body: payload,
          headers: headers
        });
        break;
      default:
        responseData = await request({
          method: method,
          url: requestUrl,
          headers: headers
        });
        break;
    }

    const { data, status, headers: responseHeaders } = responseData;

    return Promise.resolve({ data });
  }
});
