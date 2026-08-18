import { useState } from "react";
import "./App.css";

function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  const askQuestion = async () => {
    if (!question.trim()) return;

    setLoading(true);
    setAnswer("");

    try {
      const response = await fetch("https://graph-engineering-api.onrender.com/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_name: "Adarsh",
          question: question,
        }),
      });

      const data = await response.json();
      setAnswer(data.answer);
    } catch (error) {
      setAnswer("Unable to connect to the Graph Engineering API.");
    }

    setLoading(false);
  };

  return (
    <div className="app">

      <div className="card">

        <div className="header">
          <div className="logo">🧠</div>

          <div>
            <h1>Graph Engineering AI</h1>
            <p>Knowledge Graph Assistant</p>
          </div>
        </div>

        <div className="divider"></div>

        <div className="question-section">

          <label>Ask a question</label>

          <div className="input-row">

            <input
              type="text"
              placeholder="e.g. What skills does Adarsh know?"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  askQuestion();
                }
              }}
            />

            <button
              onClick={askQuestion}
              disabled={loading}
            >
              {loading ? "..." : "Ask"}
            </button>

          </div>

        </div>

        <div className="answer-section">

          <div className="answer-title">
            <span>🤖</span>
            <h2>Answer</h2>
          </div>

          <div className="answer">

            {loading ? (
              <p className="loading">Thinking...</p>
            ) : answer ? (
              <p>{answer}</p>
            ) : (
              <p className="empty">
                Ask something about Adarsh to get an answer from the
                knowledge graph.
              </p>
            )}

          </div>

        </div>

        <div className="footer">
          Powered by FastAPI · Groq · Neo4j
        </div>

      </div>

    </div>
  );
}

export default App;