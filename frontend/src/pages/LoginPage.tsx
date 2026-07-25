import { FormEvent, useState } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import MicroGestIcon from "../components/MicroGestIcon";
import { extrairMensagemErro } from "../services/api";

export default function LoginPage() {
  const { login, autenticado, carregando } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [erro, setErro] = useState<string | null>(null);
  const [entrando, setEntrando] = useState(false);

  if (!carregando && autenticado) {
    const destino = (location.state as { from?: string })?.from ?? "/";
    return <Navigate to={destino} replace />;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setErro(null);
    setEntrando(true);
    try {
      await login(email, senha);
      navigate("/");
    } catch (err: unknown) {
      setErro(extrairMensagemErro(err, "Não foi possível entrar. Tente novamente."));
    } finally {
      setEntrando(false);
    }
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "var(--mg-fundo)",
        fontFamily: "var(--mg-font-family)",
        padding: 20,
      }}
    >
      <div className="mg-card" style={{ width: "100%", maxWidth: 380 }}>
        <div style={{ textAlign: "center", marginBottom: 24 }}>
          <div style={{ margin: "0 auto 12px auto", width: 48, height: 48 }}>
            <MicroGestIcon size={48} />
          </div>
          <h2 style={{ margin: 0 }}>MicroGest</h2>
          <p style={{ margin: "4px 0 0 0", fontSize: 13, color: "var(--mg-cinza-600)" }}>
            Sistema Inteligente de Gestão Microbiológica
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          {erro && (
            <p style={{ color: "var(--mg-erro)", fontSize: 14, marginTop: 0 }}>{erro}</p>
          )}

          <div className="mg-field" style={{ marginBottom: 14 }}>
            <label>E-mail</label>
            <input
              type="email"
              required
              autoFocus
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div className="mg-field" style={{ marginBottom: 20 }}>
            <label>Senha</label>
            <input
              type="password"
              required
              value={senha}
              onChange={(e) => setSenha(e.target.value)}
            />
          </div>

          <button
            className="mg-btn mg-btn-primary"
            type="submit"
            disabled={entrando}
            style={{ width: "100%", justifyContent: "center" }}
          >
            {entrando ? "Entrando..." : "Entrar"}
          </button>
        </form>

        <p style={{ fontSize: 12, color: "var(--mg-cinza-400)", textAlign: "center", marginTop: 18 }}>
          Primeiro acesso? Cadastre-se pela API (POST /api/usuarios) - o primeiro usuário
          criado se torna administrador automaticamente.
        </p>
      </div>
    </div>
  );
}
