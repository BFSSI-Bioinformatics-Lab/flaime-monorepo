import React, { useEffect, useRef } from 'react';

const IndeterminateCheckbox = ({ id, checked, onChange, indeterminate, label }) => {
  const ref = useRef(null);

  useEffect(() => {
    if (ref.current) {
      ref.current.indeterminate = indeterminate;
    }
  }, [indeterminate]);

  return (
    <label>
      <input
        ref={ref}
        type="checkbox"
        checked={checked}
        onChange={onChange}
        id={id}
      />
      {label}
    </label>
  );
};

export { IndeterminateCheckbox };
