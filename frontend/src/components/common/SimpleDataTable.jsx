import React from 'react';

const SimpleDataTable = ({ rows = [], columns = [], loading = false }) => {
  console.log('SimpleDataTable chargé avec:', { rows, columns, loading });
  
  if (loading) return <div>Chargement des données...</div>;
  if (!rows || rows.length === 0) return <div>Aucune donnée</div>;
  
  return (
    <div>
      <h3>Tableau simple (fallback)</h3>
      <table border="1" cellPadding="8">
        <thead>
          <tr>
            {columns.map((col, i) => (
              <th key={i}>{col.headerName || col.field}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.slice(0, 5).map((row, i) => (
            <tr key={i}>
              {columns.map((col, j) => (
                <td key={j}>
                  {col.renderCell
                    ? col.renderCell({ row })
                    : typeof row[col.field] === "object"
                      ? "-"
                      : row[col.field]
                  }
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default SimpleDataTable;