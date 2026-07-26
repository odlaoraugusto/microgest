export interface NavItem {
  label: string;
  path: string;
  icon: string; // emoji simples no lugar de um ícone SVG, facilmente trocável depois
  implementado: boolean;
}

export const NAV_ITEMS: NavItem[] = [
  { label: "Dashboard", path: "/", icon: "📊", implementado: true },
  { label: "Pacientes", path: "/pacientes", icon: "🧑‍⚕️", implementado: true },
  { label: "Exames", path: "/exames", icon: "🧫", implementado: true },
  { label: "Antibiogramas", path: "/antibiogramas", icon: "💊", implementado: true },
  { label: "CCIH", path: "/ccih", icon: "🛡️", implementado: true },
  { label: "Relatórios", path: "/relatorios", icon: "📄", implementado: true },
  { label: "Configurações", path: "/configuracoes", icon: "⚙️", implementado: true },
];
