interface CitationLinkProps {
  index: number;
  onClick?: () => void;
}

export const CitationLink: React.FC<CitationLinkProps> = ({
  index,
  onClick,
}) => {
  if (!onClick) {
    return (
      <sup className="inline-flex items-center justify-center w-5 h-5 text-xs font-medium text-primary-600 bg-primary/10 rounded">
        {index}
      </sup>
    );
  }

  return (
    <button
      type="button"
      onClick={onClick}
      className="inline-flex items-center justify-center w-5 h-5 text-xs font-medium text-primary-600 bg-primary/10 rounded hover:bg-primary/20 transition-colors cursor-pointer"
    >
      {index}
    </button>
  );
};
