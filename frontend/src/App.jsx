import { useState, useRef, useEffect } from "react";
import "./App.css";

// App.jsx mein
  const API_URL = "https://graph-engineering-api.onrender.com";

function App() {
  const [question, setQuestion] = useState("");

  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hi! 👋 I'm Adarsh's AI assistant. Ask me anything about Adarsh's education, skills, projects, experience, or technologies.",
    },
  ]);

  const [loading, setLoading] = useState(false);

  const messagesEndRef = useRef(null);

  // =========================================
  // AUTO SCROLL
  // =========================================

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);

  // =========================================
  // ASK QUESTION
  // =========================================

  const askQuestion = async () => {
    if (!question.trim() || loading) {
      return;
    }

    const userQuestion = question.trim();

    // Add user message immediately
    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: userQuestion,
      },
    ]);

    setQuestion("");
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/ask`, {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify({
          user_name: "Adarsh",
          question: userQuestion,
        }),
      });

      const data = await response.json();

      console.log("API RESPONSE:", data);

      if (!response.ok) {
        throw new Error(
          data?.detail ||
            "Unable to get response from AI server."
        );
      }

      // =========================================
      // AI ANSWER
      // =========================================

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            data?.answer ||
            "I couldn't find an answer.",
        },
      ]);
    } catch (error) {
      console.error("ASK ERROR:", error);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "Sorry, I couldn't connect to the AI server. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  // =========================================
  // ENTER KEY
  // =========================================

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      askQuestion();
    }
  };

  // =========================================
  // UI
  // =========================================

  return (
    <div className="chat-app">

      {/* HEADER */}

      <header className="chat-header">

        <div className="header-left">

          <div className="bot-logo">
            🤖
          </div>

          <div>
            <h1>Adarsh AI</h1>

            <p>
              Personal AI Assistant
            </p>
          </div>

        </div>

        <div className="online-status">

          <span className="online-dot"></span>

          Online

        </div>

      </header>


      {/* CHAT */}

      <main className="chat-container">

        <div className="messages">

          {messages.map((message, index) => (

            <div
              key={index}
              className={
                message.role === "user"
                  ? "message user-message"
                  : "message assistant-message"
              }
            >

              {message.role === "assistant" && (
                <div className="message-avatar">
                  🤖
                </div>
              )}

              <div className="message-content">

                <div className="message-name">

                  {message.role === "user"
                    ? "You"
                    : "Adarsh AI"}

                </div>

                <div className="message-bubble">
                  {message.content}
                </div>

              </div>

            </div>

          ))}


          {/* LOADING */}

          {loading && (

            <div className="message assistant-message">

              <div className="message-avatar">
                🤖
              </div>

              <div className="message-content">

                <div className="message-name">
                  Adarsh AI
                </div>

                <div className="message-bubble typing">

                  <span></span>
                  <span></span>
                  <span></span>

                </div>

              </div>

            </div>

          )}

          <div ref={messagesEndRef}></div>

        </div>

      </main>


      {/* INPUT */}

      <footer className="chat-input-area">

        <div className="input-wrapper">

          <textarea
            value={question}
            onChange={(event) =>
              setQuestion(event.target.value)
            }
            onKeyDown={handleKeyDown}
            placeholder="Ask something about Adarsh..."
            rows={1}
            disabled={loading}
          />

          <button
            onClick={askQuestion}
            disabled={
              loading ||
              !question.trim()
            }
            className="send-button"
          >

            {loading ? "..." : "➤"}

          </button>

        </div>

        <p className="input-hint">
          Ask about Adarsh's skills, education,
          projects, experience and technologies.
        </p>

      </footer>

    </div>
  );
}

export default App;