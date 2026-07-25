interface MicroGestIconProps {
  size?: number;
  className?: string;
  /**
   * "colorido" - símbolo original (navy + verde), usar sobre fundos claros.
   * "negativo" - símbolo branco sobre fundo navy arredondado (já com o
   *   próprio fundo embutido), usar sobre superfícies escuras (ex.: sidebar).
   */
  variante?: "colorido" | "negativo";
}

/**
 * Símbolo oficial do MicroGest, vetorizado a partir do manual de
 * identidade visual (ver design/icons/). Usar sempre este componente em
 * vez de recriar o ícone ou usar emojis.
 */
export default function MicroGestIcon({
  size = 32,
  className,
  variante = "colorido",
}: MicroGestIconProps) {
  const src = variante === "negativo" ? "/simbolo-negativo.svg" : "/simbolo.svg";
  return (
    <img
      src={src}
      width={size}
      height={size}
      className={className}
      alt="MicroGest"
      style={{ display: "block" }}
    />
  );
}
