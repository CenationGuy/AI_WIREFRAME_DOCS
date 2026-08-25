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
    "http://localhost:8000/generate-dashboard",
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



import {
  Download,
  LayoutDashboard,
  Sparkles,
  FileText,
  Image as ImageIcon,
} from "lucide-react";

import {
  useState,
  useEffect,
} from "react";


const TOOL_LABELS = {
  power_bi: "Power BI",
  qlik: "Qlik Sense",
  sac: "SAP Analytics",
};


// ============================================================
// PREVIEW PANEL
// ============================================================

export default function PreviewPanel({
  phase,
  result,
  error,
  tool,
  persona,
}) {

  const [
    selectedSheet,
    setSelectedSheet
  ] = useState(0);


  // Reset selected sheet when a new result arrives

  useEffect(
    () => {

      setSelectedSheet(0);

    },
    [result]
  );


  const sheets =
    result?.generated_sheets || [];


  const currentSheet =
    sheets[selectedSheet];


  // ==========================================================
  // DOWNLOAD CURRENT IMAGE
  // ==========================================================

  const downloadCurrentImage =
    () => {

      if (
        !currentSheet?.image
      ) {
        return;
      }


      const link =
        document.createElement("a");


      link.href =
        currentSheet.image;


      link.download =
        `dashboard-sheet-${
          currentSheet.sheet_number
        }.png`;


      document.body.appendChild(
        link
      );


      link.click();


      document.body.removeChild(
        link
      );

    };


  return (

    <div className="mt-8 flex flex-col">


      {/* ================================================== */}
      {/* TOP CONTROLS */}
      {/* ================================================== */}

      <div className="mb-3 flex items-center justify-between border-b border-slate-100 pb-2.5">

        <div>

          <h2 className="text-xs font-bold uppercase tracking-wider text-slate-800">

            Canvas Preview

          </h2>


          <p className="text-[10px] text-slate-400">

            {phase === "done"

              ? `Theme: ${
                  TOOL_LABELS[tool]
                } · Persona: ${persona}`

              : "Visual rendering of generated wireframe"

            }

          </p>

        </div>


        {phase === "done" &&
          currentSheet && (

          <button
            onClick={
              downloadCurrentImage
            }
            className="flex items-center gap-1 rounded border border-slate-200 bg-white px-2 py-1 text-[11px] font-medium text-slate-700 shadow-2xs hover:bg-slate-50"
          >

            <Download size={12} />

            Export PNG

          </button>

        )}

      </div>


      {/* ================================================== */}
      {/* IDLE STATE */}
      {/* ================================================== */}

      {phase === "idle" && (

        <div className="flex min-h-[360px] flex-1 flex-col items-center justify-center rounded-lg border border-dashed border-slate-200 bg-slate-50/40 p-6 text-center">

          <div className="grid h-10 w-10 place-items-center rounded-xl bg-white text-[#E60000] shadow-2xs ring-1 ring-slate-100">

            <LayoutDashboard size={18} />

          </div>


          <h3 className="mt-2.5 text-xs font-semibold text-slate-800">

            Canvas Ready

          </h3>


          <p className="mt-0.5 max-w-xs text-[11px] text-slate-400">

            Upload a CSV and click Generate to create your
            AI-powered dashboard.

          </p>

        </div>

      )}


      {/* ================================================== */}
      {/* WORKING STATE */}
      {/* ================================================== */}

      {phase === "working" && (

        <div className="flex min-h-[360px] flex-1 flex-col items-center justify-center rounded-lg border border-slate-100 bg-slate-50/30 p-6 text-center">

          <div className="relative flex h-10 w-10 items-center justify-center">

            <div className="absolute h-full w-full animate-ping rounded-full bg-rose-200 opacity-60" />

            <div className="grid h-8 w-8 place-items-center rounded-full bg-[#E60000] text-white shadow-2xs">

              <Sparkles
                size={15}
                className="animate-spin"
              />

            </div>

          </div>


          <div className="mt-3 text-xs font-semibold text-slate-800">

            Generating Dashboard

          </div>


          <div className="mt-0.5 max-w-sm text-[10px] text-slate-400">

            Analyzing your CSV, planning dashboard sheets,
            and generating AI dashboard designs…

          </div>

        </div>

      )}


      {/* ================================================== */}
      {/* ERROR STATE */}
      {/* ================================================== */}

      {phase === "error" && (

        <div className="rounded-lg border border-rose-200 bg-rose-50/60 p-4 text-xs text-rose-700">

          <span className="font-semibold">

            Generation Failed:

          </span>

          {" "}

          {error}

        </div>

      )}


      {/* ================================================== */}
      {/* SUCCESS STATE */}
      {/* ================================================== */}

      {phase === "done" &&
        result && (

        <div className="space-y-5">


          {/* ============================================== */}
          {/* DASHBOARD TITLE */}
          {/* ============================================== */}

          <div>

            <h2 className="text-xl font-semibold text-slate-900">

              {
                result.dashboard_spec
                  ?.dashboard_title ||
                "Generated Dashboard"
              }

            </h2>


            <p className="mt-1 text-xs text-slate-500">

              {
                sheets.length
              }

              {" "}

              dashboard sheet

              {
                sheets.length !== 1
                  ? "s"
                  : ""
              }

              {" generated"}

            </p>

          </div>


          {/* ============================================== */}
          {/* SHEET TABS */}
          {/* ============================================== */}

          {sheets.length > 0 && (

            <div className="flex flex-wrap gap-2 border-b border-slate-200 pb-3">

              {sheets.map(
                (
                  sheet,
                  index
                ) => (

                  <button
                    key={
                      sheet.sheet_number
                    }

                    onClick={
                      () =>
                        setSelectedSheet(
                          index
                        )
                    }

                    className={
                      "rounded-lg px-3 py-2 text-xs font-medium transition " +

                      (
                        selectedSheet === index

                          ? "bg-[#E60000] text-white shadow-sm"

                          : "border border-slate-200 bg-white text-slate-600 hover:bg-slate-50"
                      )
                    }
                  >

                    Sheet {
                      sheet.sheet_number
                    }

                    {": "}

                    {
                      sheet.title
                    }

                  </button>

                )
              )}

            </div>

          )}


          {/* ============================================== */}
          {/* CURRENT DASHBOARD IMAGE */}
          {/* ============================================== */}

          {currentSheet && (

            <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">

              <div className="flex items-center gap-2 border-b border-slate-100 px-4 py-3">

                <ImageIcon
                  size={15}
                  className="text-[#E60000]"
                />

                <div>

                  <h3 className="text-sm font-semibold text-slate-800">

                    {
                      currentSheet.title
                    }

                  </h3>


                  <p className="text-[10px] text-slate-400">

                    AI-generated dashboard design

                  </p>

                </div>

              </div>


              <div className="bg-slate-100 p-3">

                <img
                  src={
                    currentSheet.image
                  }

                  alt={
                    currentSheet.title
                  }

                  className="h-auto w-full rounded-lg"
                />

              </div>

            </div>

          )}


          {/* ============================================== */}
          {/* DASHBOARD SUMMARY */}
          {/* ============================================== */}

          {result.dashboard_summary && (

            <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">

              <div className="flex items-center gap-2">

                <FileText
                  size={16}
                  className="text-[#E60000]"
                />

                <h3 className="text-sm font-semibold text-slate-800">

                  Dashboard Summary

                </h3>

              </div>


              <div className="mt-3 whitespace-pre-line text-xs leading-6 text-slate-600">

                {
                  result.dashboard_summary
                }

              </div>

            </div>

          )}


          {/* ============================================== */}
          {/* NO SHEETS FALLBACK */}
          {/* ============================================== */}

          {sheets.length === 0 && (

            <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-xs text-amber-700">

              Dashboard generation completed, but no generated
              sheet images were returned.

            </div>

          )}

        </div>

      )}

    </div>

  );

}
  

}
