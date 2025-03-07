import { SquareButtonWithIcon } from '@/components/squareButtonWithIcon';
import { IFilterInputSettingV2, IFilterItemSettingV2 } from '@/interfaces';
import { CloseOutlined } from '@ant-design/icons';
import { useSelect } from '@refinedev/antd';
import { DatePicker, Flex, Form, Input, InputNumber, Select, Slider } from 'antd';
import { SliderRangeProps } from 'antd/lib/slider';
import { ValueType } from 'rc-input-number';
import React from 'react';
import * as SolarIconSet from 'solar-icon-set';
import styled from 'styled-components';

interface AdvanceFilterFormProps {
  form?: any;
  filters?: IFilterItemSettingV2['advanceFilters'];
  totalResults: number;
  setIsOpen: React.Dispatch<React.SetStateAction<boolean>>;
  isOpen: boolean;
  handleApplyFilter?: () => void;
  handleClearAll?: () => void;
}

export const AdvanceFilterForm: React.FC<AdvanceFilterFormProps> = props => {
  const { form, filters, totalResults, setIsOpen, isOpen, handleApplyFilter, handleClearAll } = props;

  const { RangePicker } = DatePicker;

  const renderFilterItem = (filter: IFilterInputSettingV2) => {
    let elementInput;

    const { optionSelect, multipleInput } = filter;

    // case select
    if (optionSelect?.resource || multipleInput) {
      const { selectProps: selectPropResource } = optionSelect
        ? useSelect({
            resource: optionSelect.resource as any,
            optionLabel: optionSelect.optionLabel as any,
            optionValue: optionSelect.optionValue as any
          })
        : { selectProps: {} };

      let searchSelectProps: object = {
        mode: 'tags',
        showSearch: true,
        ...selectPropResource
      };

      return (
        <CustomFormItem label={filter.nameShow} name={filter.fields}>
          <Select labelInValue optionFilterProp='label' placeholder='Please Select' {...searchSelectProps} />
        </CustomFormItem>
      );
    }

    // case slider
    if (filter.fieldType === 'slider') {
      const { sliderProps } = filter;
      let childElement = [];

      const defaultSliderProps: SliderRangeProps = {
        range: true,
        min: 0,
        max: 100,
        defaultValue: [50, 100],
        step: 1
      };

      const { range, min, max, defaultValue, step } = sliderProps ?? defaultSliderProps;

      if (filter.children) {
        let minField: string, maxField: string;
        filter.children.forEach(child => {
          if (child.operator === 'gte') {
            minField = child.fields;
          } else if (child.operator === 'lte') {
            maxField = child.fields;
          }
        });

        const handleChange = (value: ValueType | null, isMin: boolean) => {
          form.current.validateFields();
          if (isMin) {
            if (value === null) {
              form.current.setFieldValue(filter.fields, [0, form.current.getFieldValue(maxField)]);
            } else {
              if (value < form.current.getFieldValue(maxField)) {
                form.current.setFieldValue(filter.fields, [value, form.current.getFieldValue(maxField)]);
              }
            }
          } else {
            if (value === null) {
              form.current.setFieldValue(filter.fields, [form.current.getFieldValue(minField), max]);
            } else {
              if (value > form.current.getFieldValue(minField)) {
                form.current.setFieldValue(filter.fields, [form.current.getFieldValue(minField), value]);
              }
            }
          }
        };

        const validateMin = () => (_: any, value: number) => {
          const max = form.current.getFieldValue(maxField);

          if (value !== null && max !== null && value > max) {
            return Promise.reject(new Error('Min value cannot be greater than max value'));
          }
          return Promise.resolve();
        };

        const validateMax = () => (_: any, value: number) => {
          const min = form.current.getFieldValue(minField);
          if (value !== null && min !== null && value < min) {
            return Promise.reject(new Error('Max value cannot be less than min value'));
          }
          return Promise.resolve();
        };

        for (const child of filter.children) {
          const isMin = child.operator === 'gte';
          const validate = isMin ? validateMin() : validateMax();

          childElement.push(
            <CustomFormItem label={child.nameShow} name={child.fields} rules={[{ validator: validate }]}>
              <InputNumber
                placeholder={child.nameShow}
                onChange={value => handleChange(value, isMin)}
                style={{ width: '100%' }}
              />
            </CustomFormItem>
          );
        }
      }

      return (
        <>
          <CustomFormItem label={filter.nameShow} name={filter.fields}>
            <Slider
              range={range}
              min={min}
              max={max}
              step={step}
              onChange={value => {
                filter.children &&
                  form.current?.setFieldsValue({
                    [filter.children[0]?.fields]: value[0],
                    [filter.children[1]?.fields]: value[1]
                  });
                form.current.validateFields();
              }}
            />
          </CustomFormItem>
          {filter.children && (
            <Flex align='center' justify='space-between' gap={8}>
              {childElement}
            </Flex>
          )}
        </>
      );
    }

    // case datetime
    if (filter.operator === 'between' && filter.fieldType === 'datetime') {
      elementInput = (
        <RangePicker
          showTime={true}
          format={'YYYY/MM/DD HH:mm:ss'}
          suffixIcon={<SolarIconSet.CalendarMinimalistic color={'var(--neutral_07)'} size={18} iconStyle='Outline' />}
        />
      );
    }

    // case date
    if (filter.operator === 'between' && filter.fieldType === 'date') {
      elementInput = (
        <RangePicker
          format={'YYYY/MM/DD'}
          style={{ width: '100%' }}
          suffixIcon={<SolarIconSet.CalendarMinimalistic color={'var(--neutral_07)'} size={18} iconStyle='Outline' />}
        />
      );
    }

    // case default
    if (!elementInput) {
      elementInput = <Input placeholder={filter.nameShow} />;
    }

    return (
      <CustomFormItem label={filter.nameShow} name={filter.fields}>
        {elementInput}
      </CustomFormItem>
    );
  };

  return (
    <AdvanceFilterComponentDiv $isOpen={isOpen}>
      <TitleDiv>
        <div>Advance Filter</div>
        <CloseOutlined style={{ color: 'var(--neutral_07)' }} onClick={() => setIsOpen(false)} />
      </TitleDiv>
      <CustomDiv>{filters?.map(filter => renderFilterItem(filter))}</CustomDiv>
      <Flex align='center' gap='8' justify='space-between' style={{ padding: '8px 16px' }}>
        <TotalResultDiv>Show {totalResults} results</TotalResultDiv>
        <Flex align='center' gap={8}>
          <SquareButtonWithIcon onClick={handleClearAll}>Clear all</SquareButtonWithIcon>
          <SquareButtonWithIcon type='primary' onClick={handleApplyFilter}>
            Apply all filters
          </SquareButtonWithIcon>
        </Flex>
      </Flex>
    </AdvanceFilterComponentDiv>
  );
};

const AdvanceFilterComponentDiv = styled.div<{ $isOpen?: boolean }>`
  position: absolute;
  background-color: white;
  width: 432px;
  left: 175px;
  top: 160px;
  border: 1px solid var(--neutral_09);
  box-shadow: 1px 1px 5px var(--neutral_09);
  z-index: 100;
  display: ${props => (props.$isOpen ? '' : 'none')};
`;

const CustomDiv = styled.div`
  padding: 16px;
  border-bottom: 1px solid var(--neutral_10);
`;

const CustomFormItem = styled(Form.Item)`
  .ant-form-item-control {
    margin-bottom: -8px;
  }
  width: 100%;
`;

const TitleDiv = styled(Flex)`
  padding: 8px 16px;
  justify-content: space-between;
  font-size: 16px;
  font-weight: 500;
  border-bottom: 1px solid var(--neutral_10);
`;

const TotalResultDiv = styled.div`
  color: var(--neutral_06);
`;
