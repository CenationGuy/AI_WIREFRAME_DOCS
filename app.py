import { useState } from "react";

import Sidebar from "./components/Sidebar.jsx";
import TopBar from "./components/TopBar.jsx";
import GeneratorForm from "./components/GeneratorForm.jsx";
import PreviewPanel from "./components/PreviewPanel.jsx";


const INITIAL_SESSIONS = [
  { id: 1, title: "Q2 sales overview", market: "DE", when: "Today" },
  { id: 2, title: "Retail footfall by store", market: "UK", when: "Today" },
  { id: 3, title: "Churn drivers — enterprise", market: "APAC", when: "Yesterday" },
  { id: 4, title: "Marketing spend vs pipeline", market: "US", when: "Yesterday" },
  { id: 5, title: "Inventory turns by category", market: "DE", when: "Previous 7 days" },
  { id: 6, title: "NPS trend, rolling 12m", market: "FR", when: "Previous 7 days" },
];


// ============================================================
// REAL BACKEND API CALL
// ============================================================

async function generateDashboard({
  file,
  persona,
  tool,
  instructions,
}) {

  if (!file) {
    throw new Error("Please upload a CSV file first.");
  }


  // ----------------------------------------------------------
  // CREATE FORM DATA
  //
  // FastAPI expects:
  //
  // file: UploadFile = File(...)
  // ----------------------------------------------------------

  const formData = new FormData();

  formData.append(
    "file",
    file
  );


  // ----------------------------------------------------------
  // CALL FASTAPI
  // ----------------------------------------------------------

  const response = await fetch(
    "/api/generate-dashboard",
    {
      method: "POST",
      body: formData,
    }
  );


  // ----------------------------------------------------------
  // HANDLE ERRORS
  // ----------------------------------------------------------

  if (!response.ok) {

    let errorMessage =
      "Dashboard generation failed.";

    try {

      const errorData =
        await response.json();

      errorMessage =
        errorData.detail ||
        errorMessage;

    } catch {

      // Keep default error message

    }

    throw new Error(
      errorMessage
    );
  }


  // ----------------------------------------------------------
  // RETURN BACKEND RESPONSE
  // ----------------------------------------------------------

  const data =
    await response.json();

  return data;
}


// ============================================================
// APP
// ============================================================

export default function App() {

  const [
    sessions,
    setSessions
  ] = useState(
    INITIAL_SESSIONS
  );


  const [
    activeId,
    setActiveId
  ] = useState(
    INITIAL_SESSIONS[0].id
  );


  const [
    query,
    setQuery
  ] = useState("");


  const [
    persona,
    setPersona
  ] = useState(
    "Executive"
  );


  const [
    tool,
    setTool
  ] = useState(
    "power_bi"
  );


  const [
    file,
    setFile
  ] = useState(null);


  const [
    instructions,
    setInstructions
  ] = useState("");


  const [
    phase,
    setPhase
  ] = useState("idle");


  const [
    result,
    setResult
  ] = useState(null);


  const [
    error,
    setError
  ] = useState("");


  const active =
    sessions.find(
      (session) =>
        session.id === activeId
    ) || null;


  // ==========================================================
  // CREATE NEW DASHBOARD SESSION
  // ==========================================================

  const handleNew = () => {

    const id =
      Date.now();


    setSessions(
      (previous) => [
        {
          id,
          title: "Untitled dashboard",
          market: "DE",
          when: "Today",
        },
        ...previous,
      ]
    );


    setActiveId(id);

    setFile(null);

    setInstructions("");

    setPhase("idle");

    setResult(null);

    setError("");
  };


  // ==========================================================
  // GENERATE DASHBOARD
  // ==========================================================

  const handleGenerate =
    async () => {

      setPhase(
        "working"
      );

      setError("");

      setResult(
        null
      );


      try {

        const response =
          await generateDashboard({
            file,
            persona,
            tool,
            instructions,
          });


        console.log(
          "Backend response:",
          response
        );


        setResult(
          response
        );


        // ----------------------------------------------------
        // OPTIONAL:
        // UPDATE SESSION TITLE USING GENERATED DASHBOARD TITLE
        // ----------------------------------------------------

        if (
          response.dashboard_spec?.dashboard_title
        ) {

          setSessions(
            (previous) =>
              previous.map(
                (session) =>
                  session.id === activeId
                    ? {
                        ...session,
                        title:
                          response.dashboard_spec
                            .dashboard_title,
                      }
                    : session
              )
          );

        }


        setPhase(
          "done"
        );

      } catch (error) {

        console.error(
          "Dashboard generation error:",
          error
        );


        setError(
          error.message ||
          "Something went wrong."
        );


        setPhase(
          "error"
        );

      }

    };


  // ==========================================================
  // UI
  // ==========================================================

  return (

    <div className="flex h-screen w-full bg-slate-50 text-sm text-slate-800 antialiased">

      <Sidebar
        sessions={sessions}
        activeId={activeId}
        query={query}
        onQuery={setQuery}
        onSelect={setActiveId}
        onNew={handleNew}
      />


      <main className="flex min-w-0 flex-1 flex-col">

        <TopBar
          title={
            active
              ? active.title
              : "New dashboard"
          }
          market={
            active?.market || "DE"
          }
        />


        <div className="flex-1 overflow-y-auto">

          <div className="mx-auto max-w-5xl px-8 py-9">

            <h1 className="text-2xl font-semibold text-slate-900">
              Create a dashboard
            </h1>


            <p className="mt-1.5 max-w-2xl text-slate-500">

              Upload a CSV file and generate an AI-powered
              dashboard with one or more dashboard sheets.

            </p>


            <GeneratorForm
              persona={persona}
              setPersona={setPersona}

              tool={tool}
              setTool={setTool}

              file={file}
              setFile={setFile}

              instructions={instructions}
              setInstructions={setInstructions}

              phase={phase}

              onGenerate={
                handleGenerate
              }
            />


            <PreviewPanel
              phase={phase}
              result={result}
              error={error}
              tool={tool}
              persona={persona}
            />

          </div>

        </div>

      </main>

    </div>

  );

}
