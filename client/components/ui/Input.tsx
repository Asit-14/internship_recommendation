import { ChangeEvent, InputHTMLAttributes, SelectHTMLAttributes } from 'react';

export type SelectOption = {
  label: string;
  value: string;
};

type InputProps = {
  id: string;
  label: string;
  value?: string;
  onChange: (event: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => void;
  type?: 'text' | 'email' | 'password' | 'select' | 'file';
  placeholder?: string;
  options?: SelectOption[];
  required?: boolean;
  name?: string;
  error?: string;
  disabled?: boolean;
  accept?: string;
  multiple?: boolean;
  className?: string;
} & Omit<InputHTMLAttributes<HTMLInputElement>, 'onChange' | 'value' | 'id'> & 
    Omit<SelectHTMLAttributes<HTMLSelectElement>, 'onChange' | 'value' | 'id'>;

const fieldClassName =
  'w-full rounded-md border border-gray-300 bg-white px-3.5 py-2.5 text-sm text-gray-800 shadow-sm outline-none transition-all duration-200 placeholder:text-gray-400 focus:border-[#11486b] focus:ring-2 focus:ring-[#11486b]/20 disabled:cursor-not-allowed disabled:opacity-60';

const fileFieldClassName =
  'w-full rounded-md border border-gray-300 bg-white px-3.5 py-2.5 text-sm text-gray-800 shadow-sm outline-none transition-all duration-200 file:mr-3 file:rounded-md file:border-0 file:bg-[#ffa425] file:px-3 file:py-1.5 file:text-xs file:font-semibold file:text-black hover:file:bg-[#e6951f] focus:border-[#11486b] focus:ring-2 focus:ring-[#11486b]/20 disabled:cursor-not-allowed disabled:opacity-60';

export function Input({
  id,
  label,
  value,
  onChange,
  type = 'text',
  placeholder,
  options = [],
  required = false,
  name,
  error,
  disabled = false,
  accept,
  multiple = false,
  className,
  ...props
}: InputProps) {
  const fieldId = id;
  const errorId = `${id}-error`;

  return (
    <div className="flex flex-col gap-1.5">
      <label htmlFor={fieldId} className="text-sm font-semibold text-gray-700">
        {label}
        {required && <span className="ml-0.5 text-[#da6328]">*</span>}
      </label>

      {type === 'select' ? (
        <select
          id={fieldId}
          name={name ?? id}
          value={value}
          onChange={onChange}
          required={required}
          disabled={disabled}
          aria-invalid={!!error}
          aria-describedby={error ? errorId : undefined}
          className={`${fieldClassName} ${className || ''}`}
          {...(props as SelectHTMLAttributes<HTMLSelectElement>)}
        >
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      ) : type === 'file' ? (
        <input
          id={fieldId}
          name={name ?? id}
          type="file"
          onChange={onChange}
          required={required}
          disabled={disabled}
          accept={accept}
          multiple={multiple}
          aria-invalid={!!error}
          aria-describedby={error ? errorId : undefined}
          className={`${fileFieldClassName} ${error ? 'border-[#ac2b49] focus:border-[#ac2b49] focus:ring-[#ac2b49]/20' : ''} ${className || ''}`}
          {...(props as InputHTMLAttributes<HTMLInputElement>)}
        />
      ) : (
        <input
          id={fieldId}
          name={name ?? id}
          type={type}
          value={value ?? ''}
          onChange={onChange}
          required={required}
          disabled={disabled}
          placeholder={placeholder}
          autoComplete="off"
          aria-invalid={!!error}
          aria-describedby={error ? errorId : undefined}
          className={`${fieldClassName} ${error ? 'border-[#ac2b49] focus:border-[#ac2b49] focus:ring-[#ac2b49]/20' : ''} ${className || ''}`}
          {...(props as InputHTMLAttributes<HTMLInputElement>)}
        />
      )}

      {error && (
        <p id={errorId} className="text-xs font-medium text-[#ac2b49]" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}
