import { toast } from 'react-hot-toast';

const baseClassName = 'rounded-md border bg-white px-4 py-3 text-sm font-medium shadow-lg';

export const showSuccess = (message: string) =>
  toast.success(message, {
    className: `${baseClassName} border-[#478356] text-[#478356]`,
  });

export const showError = (message: string) =>
  toast.error(message, {
    className: `${baseClassName} border-[#ac2b49] text-[#ac2b49]`,
  });

export const showInfo = (message: string) =>
  toast(message, {
    icon: 'i',
    className: `${baseClassName} border-[#11486b] text-[#11486b]`,
  });
