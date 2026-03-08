import { useState } from "react";
import { Sidebar } from "./Sidebar";
import { ReferencePanel } from "./ReferencePanel";

interface AppLayoutProps {
  children: React.ReactNode;
}

export const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const [isRefPanelOpen, setIsRefPanelOpen] = useState(false);

  return (
    <div className="flex h-screen w-full bg-background">
      {/* 左侧边栏 */}
      <Sidebar className="w-64 flex-shrink-0" />

      {/* 主内容区 */}
      <main className="flex-1 flex flex-col min-w-0">
        {children}
      </main>

      {/* 右侧引用面板 */}
      <ReferencePanel
        isOpen={isRefPanelOpen}
        onClose={() => setIsRefPanelOpen(false)}
        className="w-96 flex-shrink-0"
      />
    </div>
  );
};
