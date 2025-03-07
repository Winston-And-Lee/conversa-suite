import { BaseRecord, CrudFilters } from '@refinedev/core';

import { useTable } from '@refinedev/antd';

import { filterSettingMapper } from '@/components/autoRender/filter';
import { IFilterInputSetting, IUseFilterTableProps } from '@/interfaces';

export function useFilterTable<T extends BaseRecord>(props: IUseFilterTableProps<T>) {
  const {
    resource: resourceFromProp,
    initialPageSize: initialPageSizeFromProp,
    filters: filtersFromProp,
    sorters: sortersFromProp,
    queryOptions: queryOptionsFromProp
  } = props;

  let filterSettings: IFilterInputSetting[] = [];
  if (props.advances) {
    filterSettings = [...props.advances];
  }
  if (props.simple) {
    filterSettings.push(props.simple);
  }

  const filterSettingsMap = filterSettingMapper(filterSettings);

  const { tableProps, filters, searchFormProps, tableQueryResult, setCurrent } = useTable<T>({
    resource: resourceFromProp,
    filters: filtersFromProp,
    sorters: sortersFromProp,
    initialPageSize: initialPageSizeFromProp,
    queryOptions: queryOptionsFromProp,
    syncWithLocation: true,
    pagination: {
      pageSize: 20
    },

    onSearch: (params: any) => {
      const crudFilters: CrudFilters = [];

      const dataSchema = tableQueryResult?.data?.schema;
      const mainDataSchema = dataSchema?.['main'];
      const fieldSchemaMap: any = {};
      mainDataSchema?.fields.forEach((obj: any) => {
        fieldSchemaMap[obj.name] = obj;
      });

      Object.keys(params).forEach(key => {
        const filterValue = params[key];
        const filterSetting = filterSettingsMap[key];

        if (filterSetting.operator == 'between') {
          let startValue;
          let endValue;

          if (filterValue) {
            startValue = filterValue[0];
            endValue = filterValue[1];

            if (fieldSchemaMap?.[key]?.type == 'datetime') {
              startValue = new Date(filterValue[0]).toISOString();
              endValue = new Date(filterValue[1]).toISOString();
            }
          }
          crudFilters.push({
            field: key,
            operator: 'gte',
            value: startValue
          });
          crudFilters.push({
            field: key,
            operator: 'lte',
            value: endValue
          });
          return;
        }

        crudFilters.push({
          field: key,
          operator: filterSetting.operator,
          value: filterValue
        });
      });
      return crudFilters;
    }
  });

  const filterProps = {
    ...props,
    filters: filters,
    dataSchema: tableQueryResult?.data?.schema,
    searchFormProps: searchFormProps
  };

  return {
    filterProps,
    tableProps,
    filters,
    searchFormProps,
    tableQueryResult,
    dataSchema: filterProps.dataSchema,
    setCurrent
  };
}

// export type CrudOperators =
//     | "eq"
//     | "ne"
//     | "lt"
//     | "gt"
//     | "lte"
//     | "gte"
//     | "in"
//     | "nin"
//     | "contains"
//     | "ncontains"
//     | "containss"
//     | "ncontainss"
//     | "between"
//     | "nbetween"
//     | "null"
//     | "nnull"
//     | "startswith"
//     | "nstartswith"
//     | "startswiths"
//     | "nstartswiths"
//     | "endswith"
//     | "nendswith"
//     | "endswiths"
//     | "nendswiths"
//     | "or"
//     | "and";
