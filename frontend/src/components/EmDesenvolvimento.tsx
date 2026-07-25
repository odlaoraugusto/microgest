interface EmDesenvolvimentoProps {
  modulo: string;
  sprint: string;
  descricao: string;
}

export default function EmDesenvolvimento({
  modulo,
  sprint,
  descricao,
}: EmDesenvolvimentoProps) {
  return (
    <div
      className="mg-card"
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "flex-start",
        gap: 10,
        maxWidth: 560,
      }}
    >
      <span className="mg-badge mg-badge-info">{sprint}</span>
      <h3 style={{ margin: 0 }}>Módulo {modulo}</h3>
      <p style={{ margin: 0, color: "var(--mg-cinza-600)", fontSize: 14, lineHeight: 1.6 }}>
        {descricao}
      </p>
      <p style={{ margin: 0, color: "var(--mg-cinza-400)", fontSize: 13 }}>
        A estrutura do backend (router/service/repository) já está criada em{" "}
        <code>backend/app/routers/</code>. Seguir o mesmo padrão do módulo Pacientes
        para implementar.
      </p>
    </div>
  );
}
