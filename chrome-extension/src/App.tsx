import { useState } from "react";
import ChatInterface from "./views/ChatInterface";
import axios from "axios";

export default function App() {
  const [chatStarted, setChatStarted] = useState(false);
  const [initialBotMessage, setInitialBotMessage] = useState<string | null>(null);

  const handleAnalyzeClick = async () => {
    try {
      chrome.tabs.query({ active: true, currentWindow: true }, async (tabs) => {
        const url = tabs[0]?.url;
        console.log("Current tab URL:", url);
        if (!url || !url.includes("youtube.com/watch")) {
          alert("Please open a YouTube video tab.");
          return;
        }

        const urlObj = new URL(url);
        const videoId = urlObj.searchParams.get("v");

        if (!videoId) {
          alert("Could not extract video ID.");
          return;
        }

        const response = await axios.post("http://localhost:8000/analyze", {
          message: videoId,
        });

        setInitialBotMessage(response.data.reply);
        setChatStarted(true);
      });
    } catch (err) {
      console.error("Error analyzing video:", err);
      alert("Something went wrong.");
    }
  };

  return (
    <div className="h-[500px] w-[300px] bg-zinc-900 text-white p-4">
      {chatStarted ? (
        <ChatInterface initialBotMessage={initialBotMessage} />
      ) : (
        <div className="flex flex-col items-center justify-center h-full space-y-4">
          <h2 className="text-lg font-semibold">AI Video Analyzer</h2>
          <button
            onClick={handleAnalyzeClick}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
          >
            Analyze Video
          </button>
        </div>
      )}
    </div>
  );
}
