import "./styles/globals.css";
import DynamicScene from "./components/DynamicScene";
import useInterview from "./hooks/useInterview";
import InterviewPage from "./pages/InterviewPage";
import ReportPage from "./pages/ReportPage";
import SetupPage from "./pages/SetupPage";

export default function App() {
  const interview = useInterview();

  return (
    <div className="app-shell">
      <DynamicScene phase={interview.phase} />
      <div className="content-layer">
        {interview.phase === "setup" && (
          <SetupPage
            onStart={interview.startInterview}
            loading={interview.loading}
            error={interview.error}
            onRegister={interview.register}
            onLogin={interview.login}
            authReady={interview.authReady}
            history={interview.history}
            onRefreshHistory={interview.refreshHistory}
            onRunGapAnalysis={interview.runGapAnalysis}
            gapAnalysis={interview.gapAnalysis}
            onGetRunDetail={interview.getRunDetail}
            historyDetail={interview.historyDetail}
            onRefreshObservability={interview.refreshObservability}
            observability={interview.observability}
          />
        )}
        {interview.phase === "interview" && (
          <InterviewPage
            jdAnalysis={interview.jdAnalysis}
            questions={interview.questions}
            currentIndex={interview.currentIndex}
            evaluations={interview.evaluations}
            loading={interview.loading}
            onSubmit={interview.submitAnswer}
            onTranscript={interview.appendTranscript}
            error={interview.error}
          />
        )}
        {interview.phase === "report" && <ReportPage report={interview.report} onReset={interview.reset} />}
      </div>
    </div>
  );
}

