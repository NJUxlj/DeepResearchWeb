import { Sidebar } from "./Sidebar";
import { ReferencePanel } from "./ReferencePanel";
import { useReferenceStore } from "@/stores/referenceStore";

interface AppLayoutProps {
  children: React.ReactNode;
}

export const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const isPanelOpen = useReferenceStore((state) => state.isPanelOpen);
  const setPanelOpen = useReferenceStore((state) => state.setPanelOpen);

  return (
    <div className="flex h-screen w-full bg-background">
      {/* 左侧边栏 */}
      <Sidebar className="w-64 flex-shrink-0 max-lg:hidden" />

      {/* 主内容区 */}
      <main className="flex-1 flex flex-col min-w-0">
        {children}
      </main>

      {/* 右侧引用面板 */}
      <ReferencePanel
        isOpen={isPanelOpen}
        onClose={() => setPanelOpen(false)}
        className="w-96 flex-shrink-0 max-lg:hidden"
      />
    </div>
  );
};
