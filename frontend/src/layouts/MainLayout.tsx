import { ReactNode } from "react";
import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";

interface MainLayoutProps {
  titulo: string;
  subtitulo?: string;
  children: ReactNode;
}

export default function MainLayout({ titulo, subtitulo, children }: MainLayoutProps) {
  return (
    <div className="mg-app-shell">
      <Sidebar />
      <div className="mg-main">
        <Topbar titulo={titulo} subtitulo={subtitulo} />
        <div className="mg-content">{children}</div>
      </div>
    </div>
  );
}
