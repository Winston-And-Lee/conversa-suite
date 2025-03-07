export type ColorMode = 'default' | 'secondary' | 'green' | 'blue' | 'pink' | 'red' | 'orange' | 'lightBlue' | 'yellow';

export const COLORS = {
  default: {
    primary_01: '#001F3D', // Main dark blue
    primary_02: '#00335E', // Slightly lighter blue
    primary_03: '#00497E', // Mid-tone blue
    primary_04: '#F4AE75', // Main accent peach
    primary_05: '#FAD7B2', // Lighter accent peach
    secondary_01: '#7FB3D5', // Soft blue complement
    secondary_02: '#EDEEF2', // Light background
    accent_01: '#FFC07F', // Vibrant accent for highlights
    accent_02: '#FFC493', // Light peach for accents
    neutral_07: '#98A2B3',
    neutral_08: '#D0D5DD',
    neutral_10: '#e4e7ec',
    neutral_12: '#FCFCFD',
    neutral_13: '#FFFFFF'
  },
  secondary: {
    primary_01: '#0FF',
    primary_02: '#00F',
    primary_03: '#00497E',
    primary_04: '#F4AE75',
    primary_05: '#FAD7B2',
    secondary_01: '#7FB3D5',
    secondary_02: '#EDEEF2',
    accent_01: '#FFC07F',
    accent_02: '#FFC493',
    neutral_07: '#98A2B3',
    neutral_08: '#D0D5DD',
    neutral_10: '#e4e7ec',
    neutral_12: '#FCFCFD',
    neutral_13: '#FFFFFF'
  },
  green: {
    primary_01: '#52C41A', // Green
    primary_02: '#73D13D', // Lighter green
    primary_03: '#95DE64', // Light green
    primary_04: '#D9F7BE', // Soft green background
    primary_05: '#F6FFED', // Very faint green
    secondary_01: '#C6E9A6', // Soft green complement
    secondary_02: '#EFF7E6', // Light green background
    accent_01: '#6DD15C', // Vibrant green for highlights
    accent_02: '#8BE47B', // Light green for accents
    neutral_07: '#98A2B3',
    neutral_08: '#D0D5DD', // Neutral complement
    neutral_10: '#e4e7ec',
    neutral_12: '#FCFCFD', // Neutral background
    neutral_13: '#FFFFFF'
  },
  blue: {
    primary_01: '#2F54EB', // Deep Blue
    primary_02: '#597EF7', // Medium Blue
    primary_03: '#85A5FF', // Light Blue
    primary_04: '#D6E4FF', // Very Light Blue
    primary_05: '#F0F5FF', // Soft blue background
    secondary_01: '#A7C2FF', // Soft blue complement
    secondary_02: '#EFF4FF', // Light blue background
    accent_01: '#3F75FF', // Vibrant blue for highlights
    accent_02: '#679BFF', // Light blue for accents
    neutral_07: '#98A2B3',
    neutral_08: '#D0D5DD', // Neutral complement
    neutral_10: '#e4e7ec',
    neutral_12: '#FCFCFD', // Neutral background
    neutral_13: '#FFFFFF'
  },
  pink: {
    primary_01: '#EB2F96', // Vibrant Pink
    primary_02: '#F759AB', // Medium Pink
    primary_03: '#FF85C0', // Soft Pink
    primary_04: '#FFD6E7', // Light Pink
    primary_05: '#FFF0F6', // Very Faint Pink
    secondary_01: '#F5A3D1', // Soft pink complement
    secondary_02: '#FFEAF5', // Light pink background
    accent_01: '#FF4D9E', // Vibrant pink for highlights
    accent_02: '#FF71B6', // Light pink for accents
    neutral_07: '#98A2B3',
    neutral_08: '#D0D5DD', // Neutral complement
    neutral_10: '#e4e7ec',
    neutral_12: '#FCFCFD', // Neutral background
    neutral_13: '#FFFFFF'
  },
  red: {
    primary_01: '#FF4D4F', // Bold Red
    primary_02: '#FF7875', // Medium Red
    primary_03: '#FFA39E', // Soft Red
    primary_04: '#FFD7D6', // Light Red
    primary_05: '#FFF1F0', // Faint Red
    secondary_01: '#FFB3B3', // Soft red complement
    secondary_02: '#FFECEC', // Light red background
    accent_01: '#FF6B6B', // Vibrant red for highlights
    accent_02: '#FF8A8A', // Light red for accents
    neutral_07: '#98A2B3',
    neutral_08: '#D0D5DD', // Neutral complement
    neutral_10: '#e4e7ec',
    neutral_12: '#FCFCFD', // Neutral background
    neutral_13: '#FFFFFF'
  },
  orange: {
    primary_01: '#FA8C16', // Bright Orange
    primary_02: '#FFA940', // Medium Orange
    primary_03: '#FFC069', // Soft Orange
    primary_04: '#FFE7BA', // Light Orange
    primary_05: '#FFF7E6', // Faint Orange
    secondary_01: '#FFD0A3', // Soft orange complement
    secondary_02: '#FFF3E1', // Light orange background
    accent_01: '#FF9B30', // Vibrant orange for highlights
    accent_02: '#FFB060', // Light orange for accents
    neutral_07: '#98A2B3',
    neutral_08: '#D0D5DD', // Neutral complement
    neutral_10: '#e4e7ec',
    neutral_12: '#FCFCFD', // Neutral background
    neutral_13: '#FFFFFF'
  },
  lightBlue: {
    primary_01: '#1890FF', // Bright Light Blue
    primary_02: '#40A9FF', // Medium Light Blue
    primary_03: '#69C0FF', // Soft Light Blue
    primary_04: '#BAE7FF', // Light Light Blue
    primary_05: '#E6F7FF', // Faint Light Blue
    secondary_01: '#A8E0FF', // Soft light blue complement
    secondary_02: '#F0FBFF', // Light light blue background
    accent_01: '#3C9FFF', // Vibrant light blue for highlights
    accent_02: '#60B2FF', // Light light blue for accents
    neutral_07: '#98A2B3',
    neutral_08: '#D0D5DD', // Neutral complement
    neutral_10: '#e4e7ec',
    neutral_12: '#FCFCFD', // Neutral background
    neutral_13: '#FFFFFF'
  },
  yellow: {
    primary_01: '#FADB14', // Yellow
    primary_02: '#FFEC3D', // Medium Yellow
    primary_03: '#FFF566', // Light Yellow
    primary_04: '#FFFEB8', // Soft Yellow
    primary_05: '#FEFFE6', // Very Faint Yellow
    secondary_01: '#FFF599', // Soft yellow complement
    secondary_02: '#FFFEE3', // Light yellow background
    accent_01: '#FFDA3A', // Vibrant yellow for highlights
    accent_02: '#FFEA66', // Light yellow for accents
    neutral_07: '#98A2B3',
    neutral_08: '#D0D5DD', // Neutral complement
    neutral_10: '#e4e7ec',
    neutral_12: '#FCFCFD', // Neutral background
    neutral_13: '#FFFFFF'
  }
};
