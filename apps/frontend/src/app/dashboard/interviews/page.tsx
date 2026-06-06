import { InterviewScheduler } from "@/components/organisms/InterviewScheduler";
import { PipelineKanban } from "@/components/organisms/PipelineKanban";

export default function InterviewsPage() {
  return (
    <div className="page-pad">
      <InterviewScheduler />
      <PipelineKanban />
    </div>
  );
}
