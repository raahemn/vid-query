import { useEffect, useState } from "react";
import ChatInterface from "./views/ChatInterface";
import Header from "./components/Header";
import axios from "axios";

type Message = {
  text: string;
  sender: "user" | "bot";
};

export default function App() {
  const [chatStarted, setChatStarted] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);

  const [videoId, setVideoId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false); // Add loading state

  // Detect current video ID and load messages only for that video
  useEffect(() => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const url = tabs[0]?.url;
      if (url && url.includes("youtube.com/watch")) {
        const id = new URL(url).searchParams.get("v");
        if (id) {
          setVideoId(id);

          // Load chat history for this video only
          const videoChats = JSON.parse(
            localStorage.getItem(id) || "{}"
          );
          if (videoChats?.length) {
            setMessages(videoChats);
            setChatStarted(true);
          }
        }
      }
    });
  }, []);

  // Persist messages only when they change
  useEffect(() => {
    if (!videoId) return;

    localStorage.setItem(videoId, JSON.stringify(messages));
  }, [messages, videoId]);

  const handleAnalyzeClick = async () => {
    try {
      setLoading(true); // Start loading
      chrome.tabs.query({ active: true, currentWindow: true }, async (tabs) => {
        const url = tabs[0]?.url;
        console.log("Current tab URL:", url);
        if (!url || !url.includes("youtube.com/watch")) {
          alert("Please open a YouTube video tab.");
          setLoading(false); // Stop loading on error
          return;
        }

        const urlObj = new URL(url);
        const id = urlObj.searchParams.get("v");
        console.log("Extracted video ID:", id);
        setVideoId(id);

        console.log("Video id set in state:", videoId);

        if (!id) {
          alert("Could not extract video ID.");
          setLoading(false); // Stop loading on error
          return;
        }

        const response = await axios.post("http://localhost:8000/analyze", {
          video_id: id,
        });

        setMessages((prev) => [
          ...prev,
          { text: response.data.reply, sender: "bot" },
        ]);
        setChatStarted(true);
        setLoading(false); // Stop loading on success
      });
    } catch (err) {
      console.error("Error analyzing video:", err);
      alert("Something went wrong.");
      setLoading(false); // Stop loading on error
    }
  };

  const onClear = () => {
    if (!videoId) return;
    
    localStorage.removeItem(videoId);
    setMessages([]);
    setChatStarted(false);
  };

  return (
    <div className="h-[500px] w-[300px] bg-zinc-900 text-white p-3 flex flex-col">
      <Header showClear={chatStarted} onClear={onClear} />

      <div className="flex-1 overflow-hidden">
        {chatStarted ? (
          <ChatInterface
            messages={messages}
            videoId={videoId}
            setMessages={setMessages}
          />
        ) : (
          <div className="flex flex-col items-center justify-center h-full space-y-4 px-4">
            <h2 className="text-lg font-semibold">AI Video Analyzer</h2>
            {loading ? (
              <div className="flex flex-col items-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white mb-2"></div>
                <span>Analyzing...</span>
              </div>
            ) : (
              <button
                onClick={handleAnalyzeClick}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
              >
                Analyze Video
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
