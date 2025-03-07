import { COLORS } from '@/constant/color';
import { ColorTheme } from '@/enum';
import { default as dayjs, default as LocalizedFormat } from 'dayjs';

export const getType = (value: any) => {
  if (Array.isArray(value)) return 'array';
  return typeof value;
};

export const toStartCase = (value: string) => {
  return value
    .split('_')
    .map(s => s.charAt(0).toUpperCase() + s.slice(1))
    .join(' ');
};

export const formattedValueNumber = (value: number) => {
  return new Intl.NumberFormat('th-TH', {
    style: 'currency',
    currency: 'THB',
    currencyDisplay: 'symbol'
  }).format(value);
};
export const transformStatus = (status: string): string => {
  const transformedStatus = status
    .split('_')
    .map(word => {
      if (word === 'TO' || word === 'OF') return word.toLowerCase();

      return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
    })
    .join(' ');

  return transformedStatus;
};

export function convertStringToEnum<T extends object>(value: string, enumObj: T): T[keyof T] | undefined {
  const enumValue = (Object.values(enumObj) as unknown as string[]).find(e => e === value);
  return enumValue as T[keyof T] | undefined;
}

export const formatPhoneNumber = (number: string): string => {
  // Ensure that the input is a string and is exactly 10 digits long
  const cleaned = number.replace(/\D/g, '');

  if (cleaned.length === 10) {
    return cleaned.replace(/(\d{3})(\d{3})(\d{4})/, '$1-$2-$3');
  }

  // Return the original input if it's not 10 digits
  return number;
};

export const getBase64 = (file: File): Promise<string> =>
  new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = error => reject(error);
  });

export const convertDate = (
  dateString: string | null | undefined,
  format = 'DD/MM/YYYY, HH:mm:ss',
  locale: 'th' | 'en' = 'th'
): string => {
  dayjs.extend(LocalizedFormat);
  if (!dateString) return '-';
  const date = dayjs(dateString);
  if (!date.isValid()) return '-';

  if (locale === 'th') {
    const thaiDate = date.set('year', date.year() + 543);
    return thaiDate.format(format);
  }

  return date.format(format);
};

export const formatNumberWithCommas = <T extends number>(value: T): string => {
  return value.toLocaleString('en-US');
};

export const getThemeColorObjectByEnum = (color: string) => {
  switch (color) {
    case ColorTheme.BLUE:
      return COLORS['blue'];
    case ColorTheme.GREEN:
      return COLORS['green'];
    case ColorTheme.LIGHT_BLUE:
      return COLORS['lightBlue'];
    case ColorTheme.ORANGE:
      return COLORS['orange'];
    case ColorTheme.PINK:
      return COLORS['pink'];
    case ColorTheme.RED:
      return COLORS['red'];
    case ColorTheme.YELLOW:
      return COLORS['yellow'];
    default:
      return COLORS['default'];
  }
};

export const getThemeColorNameByEnum = (color: string) => {
  switch (color) {
    case ColorTheme.BLUE:
      return 'blue';
    case ColorTheme.GREEN:
      return 'green';
    case ColorTheme.LIGHT_BLUE:
      return 'lightBlue';
    case ColorTheme.ORANGE:
      return 'orange';
    case ColorTheme.PINK:
      return 'pink';
    case ColorTheme.RED:
      return 'red';
    case ColorTheme.YELLOW:
      return 'yellow';
    default:
      return 'default';
  }
};
