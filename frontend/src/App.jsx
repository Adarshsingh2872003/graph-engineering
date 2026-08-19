
import { useState } from "react";
import "./App.css";

const API_URL = "https://graph-engineering-api.onrender.com";

function App() {
  const [graphText, setGraphText] = useState("");
  const [userName, setUserName] = useState("Adarsh");
  const [question, setQuestion] = useState("");

  const [answer, setAnswer] = useState("");
  const [graphResult, setGraphResult] = useState(null);

  const [building, setBuilding] = useState(false);
  const [asking, setAsking] = useState(false);

  const [error, setError] = useState("");

  // =========================================
  // BUILD KNOWLEDGE GRAPH
  // =========================================

  const buildGraph = async () => {
    if (!graphText.trim()) {
      setError("Please enter some information first.");
      return;
    }

    setBuilding(true);
    setError("");
    setGraphResult(null);

    try {
      const response = await fetch(`${API_URL}/graph`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text: graphText,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to build knowledge graph.");
      }

      setGraphResult(data);
    } catch (err) {
      setError(
        err.message ||
          "Unable to connect to the Graph Engineering API."
      );
    } finally {
      setBuilding(false);
    }
  };

  // =========================================
  // ASK GRAPH AI
  // =========================================

  const askQuestion = async () => {
    if (!userName.trim()) {
      setError("Please enter your name.");
      return;
    }

    if (!question.trim()) {
      setError("Please enter a question.");
      return;
    }

    setAsking(true);
    setError("");
    setAnswer("");

    try {
      const response = await fetch(`${API_URL}/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_name: userName,
          question: question,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to get answer.");
      }

      setAnswer(data.answer);
    } catch (err) {
      setError(
        err.message ||
          "Unable to connect to the Graph Engineering API."
      );
    } finally {
      setAsking(false);
    }
  };

  return (
    <div className="app">

      {/* =====================================
          HEADER
      ====================================== */}

      <header className="app-header">

        <div className="brand">

          <div className="brand-icon">
            🧠
          </div>

          <div>
            <h1>Graph Engineering AI</h1>
            <p>
              Knowledge Graph + Graph RAG Assistant
            </p>
          </div>

        </div>

        <div className="status">
          <span className="status-dot"></span>
          AI Online
        </div>

      </header>


      {/* =====================================
          MAIN CONTENT
      ====================================== */}

      <main className="main-container">

        {/* =====================================
            CREATE GRAPH
        ====================================== */}

        <section className="panel">

          <div className="panel-header">

            <div className="panel-icon purple">
              🗂️
            </div>

            <div>
              <h2>Create Knowledge Graph</h2>

              <p>
                Enter information about a person,
                their skills, company and learning topics.
              </p>
            </div>

          </div>


          <div className="field">

            <label htmlFor="graphText">
              Information
            </label>

            <textarea
              id="graphText"
              value={graphText}
              onChange={(e) => setGraphText(e.target.value)}
              placeholder="Example:

Adarsh knows Python and JavaScript.
He is learning Graph Engineering.
He works at ABC Technologies."
              disabled={building}
            />

          </div>


          <button
            className="primary-button"
            onClick={buildGraph}
            disabled={building}
          >
            {building ? (
              <>
                <span className="spinner"></span>
                Building...
              </>
            ) : (
              <>
                🔨 Build Knowledge Graph
              </>
            )}
          </button>


          {/* GRAPH RESULT */}

          {graphResult && (
            <div className="graph-result">

              <div className="result-success">
                ✓ Knowledge Graph created successfully
              </div>

              <div className="result-grid">

                <div className="result-card">
                  <span className="result-number">
                    {graphResult.entities?.length || 0}
                  </span>

                  <span className="result-label">
                    Entities
                  </span>
                </div>

                <div className="result-card">
                  <span className="result-number">
                    {graphResult.relationships?.length || 0}
                  </span>

                  <span className="result-label">
                    Relationships
                  </span>
                </div>

              </div>

            </div>
          )}

        </section>


        {/* =====================================
            ASK GRAPH AI
        ====================================== */}

        <section className="panel">

          <div className="panel-header">

            <div className="panel-icon blue">
              💬
            </div>

            <div>
              <h2>Ask the Knowledge Graph</h2>

              <p>
                Ask questions using information
                stored in your knowledge graph.
              </p>
            </div>

          </div>


          <div className="ask-form">

            <div className="field">

              <label htmlFor="userName">
                User Name
              </label>

              <input
                id="userName"
                type="text"
                value={userName}
                onChange={(e) =>
                  setUserName(e.target.value)
                }
                placeholder="Enter user name"
                disabled={asking}
              />

            </div>


            <div className="field">

              <label htmlFor="question">
                Question
              </label>

              <div className="question-row">

                <input
                  id="question"
                  type="text"
                  value={question}
                  onChange={(e) =>
                    setQuestion(e.target.value)
                  }
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      askQuestion();
                    }
                  }}
                  placeholder="e.g. What skills does Adarsh know?"
                  disabled={asking}
                />

                <button
                  className="ask-button"
                  onClick={askQuestion}
                  disabled={asking}
                >
                  {asking ? (
                    <>
                      <span className="spinner"></span>
                      Thinking
                    </>
                  ) : (
                    "Ask AI"
                  )}
                </button>

              </div>

            </div>

          </div>


          {/* =====================================
              ANSWER
          ====================================== */}

          <div className="answer-container">

            <div className="answer-header">

              <div className="bot-icon">
                🤖
              </div>

              <div>
                <h3>Graph AI Answer</h3>

                <span>
                  Generated using your knowledge graph
                </span>
              </div>

            </div>


            <div
              className={`answer-box ${
                answer ? "has-answer" : ""
              }`}
            >

              {asking ? (

                <div className="answer-loading">

                  <span className="spinner"></span>

                  <span>
                    Searching the knowledge graph...
                  </span>

                </div>

              ) : answer ? (

                <p>{answer}</p>

              ) : (

                <div className="answer-placeholder">

                  <span>💡</span>

                  <p>
                    Ask something about {userName || "the user"}.
                  </p>

                  <small>
                    The AI will retrieve relevant information
                    from the Neo4j knowledge graph.
                  </small>

                </div>

              )}

            </div>

          </div>

        </section>


        {/* =====================================
            ERROR
        ====================================== */}

        {error && (

          <div className="error-box">

            <span>⚠️</span>

            <p>{error}</p>

            <button
              onClick={() => setError("")}
              className="close-error"
            >
              ×
            </button>

          </div>

        )}

      </main>


      {/* =====================================
          FOOTER
      ====================================== */}

      <footer className="footer">

        <span>Powered by</span>

        <strong>FastAPI</strong>

        <span>·</span>

        <strong>Groq</strong>

        <span>·</span>

        <strong>Neo4j</strong>

        <span>·</span>

        <strong>React</strong>

      </footer>

    </div>
  );
}

export default App;

