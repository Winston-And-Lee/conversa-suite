import { CrudFilters } from '@refinedev/core';

import { useTable } from '@refinedev/antd';

import { filterSettingMapperV2 } from '@/components/autoRender/filterv2';
import { IFilterInputSettingV2, IUseFilterTablePropsV2 } from '@/interfaces';

export function useFilterTableV2(props: IUseFilterTablePropsV2) {
  const {
    resource: resourceFromProp,
    initialPageSize: initialPageSizeFromProp,
    filters: filtersFromProp,
    sorters: sortersFromProp,
    queryOptions: queryOptionsFromProp,
    dataProviderName: dataProviderNameFromProp,
    syncWithLocation: syncWithLocationFromProp = true
  } = props;

  let filterSettings: IFilterInputSettingV2[] = [];
  if (props.advances) {
    filterSettings = [...props.advances];
  }
  if (props.simples) {
    filterSettings = [...filterSettings, ...props.simples];
  }

  const filterSettingsMap = filterSettingMapperV2(filterSettings);

  const { tableProps, filters, searchFormProps, tableQueryResult, setCurrent, setPageSize, setFilters } = useTable({
    resource: resourceFromProp,
    filters: filtersFromProp,
    sorters: sortersFromProp,
    initialPageSize: initialPageSizeFromProp,
    queryOptions: queryOptionsFromProp,
    syncWithLocation: syncWithLocationFromProp,
    pagination: {
      pageSize: props.initialPageSize
    },
    dataProviderName: dataProviderNameFromProp,

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

        if (filterSetting) {
          if (filterSetting.operator == 'between') {
            let startValue;
            let endValue;

            if (filterValue) {
              startValue = filterValue[0];
              endValue = filterValue[1];

              if (fieldSchemaMap?.[key]?.type == 'datetime') {
                const startDate = new Date(startValue);
                startDate.setUTCHours(0, 0, 0, 0);
                const isoStartDate = startDate.toISOString();

                const endDate = new Date(endValue);
                endDate.setUTCHours(0, 0, 0, 0);
                const isoEndDate = endDate.toISOString();

                startValue = isoStartDate;
                endValue = isoEndDate;
              }
            }
            crudFilters.push({
              field: key,
              operator: 'gte',
              value: startValue
            });

            // Check if the field type is 'slider' and
            // endValue is not equal to the max slider value
            const isSliderWithNonMaxEndValue =
              filterSetting.fieldType === 'slider' && endValue !== filterSetting.sliderProps.max;

            // If the field type is not 'slider' or it is 'slider'
            // with non-max end value, push to crudFilters
            if (isSliderWithNonMaxEndValue || filterSetting.fieldType !== 'slider') {
              crudFilters.push({
                field: key,
                operator: 'lte',
                value: endValue
              });
            }

            return;
          }

          if (filterSetting.optionSelect && filterValue) {
            const modifyFilterValue = [];
            for (const value of filterValue) {
              if (typeof value === 'object') {
                modifyFilterValue.push(value.value);
              } else {
                modifyFilterValue.push(value);
              }
            }
            crudFilters.push({
              field: key,
              operator: filterSetting.operator,
              value: modifyFilterValue
            });
            return;
          }
          crudFilters.push({
            field: key,
            operator: filterSetting.operator,
            value: filterValue
          });
        }
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
    setCurrent,
    setPageSize,
    setFilters
  };
}
