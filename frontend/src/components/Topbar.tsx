import { useAuth } from "../context/AuthContext";

interface TopbarProps {
  titulo: string;
  subtitulo?: string;
}

export default function Topbar({ titulo, subtitulo }: TopbarProps) {
  const { usuario, logout } = useAuth();
  const hora = new Date().getHours();
  const saudacao = hora < 12 ? "Bom dia" : hora < 18 ? "Boa tarde" : "Boa noite";
  const iniciais = usuario?.nome?.trim()?.charAt(0)?.toUpperCase() ?? "U";

  return (
    <header
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "16px 32px",
        background: "var(--mg-branco)",
        borderBottom: "1px solid var(--mg-cinza-200)",
      }}
    >
      <div>
        <h2 style={{ fontSize: 18, margin: 0 }}>
          {subtitulo ?? `${saudacao}${usuario ? `, ${usuario.nome.split(" ")[0]}` : ""}! 👋`}
        </h2>
        <p style={{ margin: "2px 0 0 0", fontSize: 13, color: "var(--mg-cinza-600)" }}>
          {titulo}
        </p>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
        {usuario && (
          <span style={{ fontSize: 13, color: "var(--mg-cinza-600)" }}>{usuario.perfil}</span>
        )}
        <div
          style={{
            width: 36,
            height: 36,
            borderRadius: "50%",
            background: "var(--mg-primaria)",
            color: "#fff",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontWeight: 600,
            fontSize: 14,
          }}
          title={usuario?.email}
        >
          {iniciais}
        </div>
        <button
          className="mg-btn mg-btn-outline"
          style={{ padding: "6px 12px", fontSize: 13 }}
          onClick={logout}
        >
          Sair
        </button>
      </div>
    </header>
  );
}
