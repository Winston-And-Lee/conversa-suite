import { BaseRecord, CrudFilters, CrudOperators, CrudSorting, GetListResponse, HttpError } from '@refinedev/core';
import { UseQueryOptions } from '@tanstack/react-query';
import { SliderRangeProps } from 'antd/lib/slider';
import { ReactNode } from 'react';

type SetFilterBehavior = 'merge' | 'replace';
// Filter --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

// type IFilterMethod = "eq" | "range" | "gt" | "gte" | "lt" | "lte" | "contains" | "icontains" |
// "iexact" | "isnull" | "endswith" | "iendswith" | "iexact" | "regex" | "iregex" | "startswith" | "istartswith";

export interface ISelectOptionFilter {
  resource?: string;
  values?: any[];
  optionLabel?: string;
  optionValue?: string;
}

export interface IFilterInputSetting {
  fields: string[];
  operator: CrudOperators;
  nameShow?: string;
  multipleInput?: boolean;
  optionSelect?: ISelectOptionFilter;
  // optionValues?: any[];
  // optionResourceValues?: any[];
}

export interface IFilterInputSettingV2 {
  fields: string;
  operator: CrudOperators;
  nameShow?: string;
  multipleInput?: boolean;
  optionSelect?: ISelectOptionFilter;
  fieldType?: string;
  sliderProps?: SliderRangeProps;
  children?: IFilterItemSettingV2['advanceFilters'];
}
export interface IFilterItemSetting {
  fields: string[];
  operator: CrudOperators;
  nameShow?: string;
  multipleInput?: boolean;
  optionSelect?: ISelectOptionFilter;
  fieldType?: string;
}
export interface IFilterItemSettingV2 {
  filters: {
    fields: string;
    operator: CrudOperators;
    nameShow?: string;
    multipleInput?: boolean;
    optionSelect?: ISelectOptionFilter;
    fieldType?: string;
  }[];
  advanceFilters?: {
    fields: string;
    operator: CrudOperators;
    nameShow?: string;
    multipleInput?: boolean;
    optionSelect?: ISelectOptionFilter;
    fieldType?: string;
    sliderProps?: SliderRangeProps;
  }[];
}

export interface IAutoRenderFilterProps {
  dataSchema: any;
  searchFormProps: any;
  filters: CrudFilters;
  simple?: IFilterInputSetting;
  advances?: IFilterInputSetting[];
  removeBox?: boolean;
}

export interface IAutoRenderFilterPropsV2 {
  dataSchema: any;
  searchFormProps: any;
  filters: CrudFilters;
  simples?: IFilterInputSettingV2[];
  advances?: IFilterInputSettingV2[];
  removeBox?: boolean;
  data?: any;
  defaultButton?: boolean;
  buttonList?: ReactNode[];
}

export interface IUseFilterTableProps<T extends BaseRecord> {
  initialPageSize?: number;
  resource?: string;
  simple?: IFilterInputSetting;
  advances?: IFilterInputSetting[];
  filters?: {
    initial?: CrudFilters;
    permanent?: CrudFilters;
    defaultBehavior?: SetFilterBehavior;
    mode?: 'server' | 'off';
  };
  sorters?: {
    initial?: CrudSorting;
    permanent?: CrudSorting;
    mode?: 'server' | 'off';
  };
  queryOptions?: UseQueryOptions<GetListResponse<T>, HttpError, GetListResponse<T>>;
}

export interface IUseFilterTablePropsV2 {
  initialPageSize?: number;
  resource?: string;
  simples?: IFilterInputSettingV2[];
  advances?: IFilterInputSettingV2[];
  filters?: {
    initial?: CrudFilters;
    permanent?: CrudFilters;
    defaultBehavior?: SetFilterBehavior;
    mode?: 'server' | 'off';
  };
  sorters?: {
    initial?: CrudSorting;
    permanent?: CrudSorting;
    mode?: 'server' | 'off';
  };
  queryOptions?: UseQueryOptions<GetListResponse<BaseRecord>, HttpError, GetListResponse<BaseRecord>>;
  dataProviderName?: string;
  syncWithLocation?: boolean;
}
