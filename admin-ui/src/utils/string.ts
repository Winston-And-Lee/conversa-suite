export const truncatedText = (original: string) => {
  const length = 50;
  const text = original.length > length ? original.substring(0, length) + '...' : original;

  return text;
};
