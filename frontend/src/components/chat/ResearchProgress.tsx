import { Search, FileText, CheckCircle, Loader2, Sparkles } from "lucide-react";

export type ResearchStage = "triage" | "plan" | "search" | "synthesis" | "report";

interface ProgressStep {
  id: ResearchStage;
  label: string;
  status: "pending" | "running" | "completed";
  icon: React.ReactNode;
}

interface ResearchProgressProps {
  currentStage?: ResearchStage;
}

const defaultStages: ProgressStep[] = [
  { id: "triage", label: "分析问题", status: "pending", icon: <Sparkles className="w-4 h-4" /> },
  { id: "plan", label: "制定计划", status: "pending", icon: <FileText className="w-4 h-4" /> },
  { id: "search", label: "检索信息", status: "pending", icon: <Search className="w-4 h-4" /> },
  { id: "synthesis", label: "综合分析", status: "pending", icon: <Loader2 className="w-4 h-4" /> },
  { id: "report", label: "生成报告", status: "pending", icon: <CheckCircle className="w-4 h-4" /> },
];

export const ResearchProgress: React.FC<ResearchProgressProps> = ({
  currentStage = "triage",
}) => {
  const stageOrder: ResearchStage[] = ["triage", "plan", "search", "synthesis", "report"];
  const currentIndex = stageOrder.indexOf(currentStage);

  const steps = defaultStages.map((step, index) => {
    if (index < currentIndex) {
      return { ...step, status: "completed" as const };
    } else if (index === currentIndex) {
      return { ...step, status: "running" as const };
    }
    return { ...step, status: "pending" as const };
  });

  return (
    <div className="px-6 py-3 bg-amber-50 dark:bg-amber-950/30 border-b border-amber-100 dark:border-amber-900">
      <div className="flex items-center gap-4">
        <span className="text-sm font-medium text-amber-800 dark:text-amber-200">研究进度:</span>
        <div className="flex items-center gap-2 overflow-x-auto">
          {steps.map((step, index) => (
            <div key={step.id} className="flex items-center gap-2">
              <div
                className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium whitespace-nowrap ${
                  step.status === "completed"
                    ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                    : step.status === "running"
                    ? "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400 animate-pulse"
                    : "bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400"
                }`}
              >
                {step.status === "running" ? (
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  step.icon
                )}
                <span>{step.label}</span>
              </div>
              {index < steps.length - 1 && (
                <div className="w-4 h-px bg-gray-300 dark:bg-gray-600" />
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
