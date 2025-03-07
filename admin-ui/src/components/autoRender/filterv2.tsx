import React, { Fragment, useState } from 'react';
import { useExport, useTranslate } from '@refinedev/core';
import type { FormInstance } from 'antd/es/form';
import { useSelect } from '@refinedev/antd';
import { Flex, Form, Tooltip } from 'antd';
import type { SelectProps } from 'antd';
import * as SolarIconSet from 'solar-icon-set';

import { IFilterInputSettingV2, IAutoRenderFilterPropsV2, IFilterItemSettingV2 } from '@/interfaces';
import styled, { useTheme } from 'styled-components';
import moment from 'moment';
import { formatNumberWithCommas } from '@/utils';
import { AdvanceFilterForm } from './advanceFilterForm';
import { SearchDropdownSelect, SearchInput } from './squareComponent';
import { SquareButtonWithIcon } from '../squareButtonWithIcon';

export const filterSettingMapperV2 = (filterSettings: IFilterInputSettingV2[]) => {
  const filterSettingsMap: any = {};
  filterSettings.forEach((obj: any) => {
    const filterInputNames: string[] = [];
    filterInputNames.push(obj.fields);
    filterSettingsMap[filterInputNames.join(',')] = obj;
  });
  return filterSettingsMap;
};

export const AutoRenderFilterV2: React.FC<IAutoRenderFilterPropsV2> = ({
  searchFormProps,
  filters,
  dataSchema,
  simples,
  advances,
  data,
  buttonList,
  defaultButton
}) => {
  const [searchField, setSearchField] = useState<string>(simples ? simples[0].fields : '');
  const [showAdvanceFilter, setShowAdvanceFilter] = useState<boolean>(false);

  const translate = useTranslate();
  const theme = useTheme();

  const formRef = React.useRef<FormInstance>(null);

  const mainDataSchema = dataSchema?.['main'];
  const fieldNames = mainDataSchema?.fields.map((item: any) => item.name);

  const filterSettingsMap = filterSettingMapperV2(advances || []);

  const { triggerExport, isLoading: exportLoading } = useExport({
    filters: filters,
    mapData: item => {
      return {
        seller_slug: item.seller_slug,
        seller_name: item.seller_name,
        platform_channel_slug: item.platform_channel_slug,
        platform_order_id: item.platform_order_id,
        customer_name: item.customer_name,
        customer_phone: item.customer_phone,
        order_created_at: item.order_created_at,
        status: item.status,
        // payment_status: item.payment_status,
        platform_status: item.platform_status,
        total_amount: item.total_amount
      };
    }
  });

  const onReset = () => {
    formRef.current?.resetFields();
    formRef.current?.submit();
  };

  const onRefresh = () => {
    window.location.reload();
  };

  const handleApplyAdvanceFilter = () => {
    let advanceValue: any = [];

    Object.entries(formRef.current?.getFieldsValue()).forEach(([key, val]) => {
      const filterSetting = filterSettingsMap[key];

      if (filterSetting && val) {
        if (filterSetting.fieldType?.includes('date')) {
          const [start, end] = val as [Date, Date];
          let startDate = moment(new Date(start)).format('YYYY/MM/DD');
          let endDate = moment(new Date(end)).format('YYYY/MM/DD');
          advanceValue.push({
            key: key,
            label: `${startDate} - ${endDate}`,
            value: key
          });
          return;
        }

        if (filterSetting.operator == 'between') {
          const [min, max] = val as [number, number];
          advanceValue.push({
            key: key,
            label: `฿${min} - ฿${max}`,
            value: key
          });
          return;
        }

        if (filterSetting.multipleInput) {
          const valList = val as [any];

          for (const val of valList) {
            advanceValue.push({
              key: val.key,
              label: val.label,
              value: key
            });
          }
          return;
        }

        advanceValue.push({ key: key, label: val, value: key });
      }
      formRef.current?.submit();
    });

    formRef.current?.setFieldsValue({
      advance: advanceValue
    });
  };

  const FilterItemV2Component: React.FC<IFilterItemSettingV2> = ({ filters, advanceFilters }) => {
    let fields: string[] = [];

    filters.forEach((filter: any) => {
      const fieldSplited = filter.fields.split('__');
      if (fieldNames?.includes(fieldSplited[0])) {
        fields.push(filter.fields);
      }
    });

    if (fields.length == 0) {
      return null;
    }

    const options: SelectProps['options'] = filters.map(filter => ({
      label: filter.nameShow,
      value: filter.fields
    }));

    if (advanceFilters) {
      options.push({
        label: (
          <Flex align='center' gap={8}>
            <SolarIconSet.Filter
              // color={"var(--neutral_02)"}
              size={14}
              iconStyle='Outline'
            />
            Advance Filter
          </Flex>
        ),
        value: 'advance'
      });
    }

    let selectProps: object = {
      style: { width: 200, paddingBottom: '-20px' },
      options: options
    };

    const selectedFilter = filters.find(item => item.fields === searchField);
    const { selectProps: selectPropResource } = selectedFilter?.optionSelect
      ? useSelect({
          resource: selectedFilter.optionSelect.resource as any,
          optionLabel: selectedFilter.optionSelect.optionLabel as any,
          optionValue: selectedFilter.optionSelect.optionValue as any,
          filters: selectedFilter.optionSelect.filters as any
        })
      : { selectProps: {} };

    let searchSelectProps: object = {
      style: { width: '100%' },
      mode: 'tags',
      showSearch: true,
      ...selectPropResource
    };

    const handleDeselectAdvanceFilter = (val: any) => {
      const deselectFilter = filterSettingsMap[val.value];

      if (deselectFilter === undefined) return;

      if (deselectFilter.optionSelect) {
        const filterAdvanceValue = formRef.current?.getFieldValue('advance').filter((field: any) => {
          return field.value === val.value;
        });

        const modifyValues = filterAdvanceValue.map((val: any) => {
          return { key: val.key, label: val.label, value: val.key };
        });
        formRef.current?.setFieldValue(deselectFilter?.fields, modifyValues);
      } else {
        formRef.current?.setFieldValue(deselectFilter?.fields, undefined);
        if (deselectFilter?.children) {
          deselectFilter.children.forEach((child: any) => {
            formRef.current?.setFieldValue(child.fields, undefined);
          });
        }
      }
    };

    return (
      <Flex align='center' gap={8} style={{ width: '100%' }}>
        <Flex align='flex-start' style={{ flex: 1 }}>
          <SearchDropdownSelect
            value={searchField}
            onSelect={(e: any) => {
              if (e !== searchField) {
                setSearchField(e);
                formRef.current?.resetFields();
                formRef.current?.submit();
              }
              if (e === 'advance') {
                setShowAdvanceFilter(true);
              } else {
                setShowAdvanceFilter(false);
              }
            }}
            {...selectProps}
          ></SearchDropdownSelect>
          <Form.Item name={searchField} noStyle>
            <SearchInput
              suffixIcon={null}
              placeholder='ค้นหา'
              onDeselect={val => handleDeselectAdvanceFilter(val)}
              labelInValue={searchField === 'advance' ? true : false}
              {...searchSelectProps}
            ></SearchInput>
          </Form.Item>
          <SquareButtonWithIcon htmlType='submit' type='primary'>
            <SolarIconSet.Magnifer
              // color="var(--neutral_14)"
              size={18}
              iconStyle='Outline'
            />
            {translate('buttons.search')}
          </SquareButtonWithIcon>
        </Flex>
        {formatNumberWithCommas(data.data.length ?? 0)} / {formatNumberWithCommas(data.total ?? 0)} รายการ
      </Flex>
    );
  };

  return (
    <Fragment>
      <Form ref={formRef} {...searchFormProps} layout='vertical'>
        <CustomFlex gap={80} align='center'>
          {simples && <FilterItemV2Component filters={simples} advanceFilters={advances} />}
          <Flex align='center' gap={8}>
            {buttonList && buttonList}
            {defaultButton && (
              <>
                <Tooltip title='Reset'>
                  <SquareButtonWithIcon onClick={onReset}>
                    <SolarIconSet.Backspace color={theme.colors.primary_02} size={18} iconStyle='Outline' />
                  </SquareButtonWithIcon>
                </Tooltip>
                <Tooltip title='Refresh'>
                  <SquareButtonWithIcon onClick={onRefresh}>
                    <SolarIconSet.Refresh color={theme.colors.primary_02} size={18} iconStyle='Outline' />
                  </SquareButtonWithIcon>
                </Tooltip>
                <Tooltip title='Export'>
                  <SquareButtonWithIcon onClick={triggerExport} loading={exportLoading}>
                    {!exportLoading && (
                      <SolarIconSet.Export color={theme.colors.primary_02} size={18} iconStyle='Outline' />
                    )}
                  </SquareButtonWithIcon>
                </Tooltip>
              </>
            )}
          </Flex>
          {searchField === 'advance' && (
            <AdvanceFilterForm
              form={formRef}
              filters={advances}
              totalResults={data?.total}
              setIsOpen={setShowAdvanceFilter}
              isOpen={showAdvanceFilter}
              handleClearAll={onReset}
              handleApplyFilter={handleApplyAdvanceFilter}
            />
          )}
        </CustomFlex>
      </Form>
    </Fragment>
  );
};

const CustomFlex = styled(Flex)`
  padding: 8px 16px;
  border-bottom: 1px solid var(--neutral_10);
  background-color: var(--neutral_12);
  margin-top: -16px;
`;
