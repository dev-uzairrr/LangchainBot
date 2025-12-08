'use client'

import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { ragAPI, mlAPI, toneAPI, adminAPI } from '@/lib/api'

export default function Home() {
  const [activeTab, setActiveTab] = useState('chat')
  const [chatQuery, setChatQuery] = useState('')
  const [chatLang, setChatLang] = useState('en')
  const [chatHistory, setChatHistory] = useState([])
  const [sentimentText, setSentimentText] = useState('')
  const [toneText, setToneText] = useState('')
  const [uploadFile, setUploadFile] = useState(null)

  // Chat mutation
  const chatMutation = useMutation({
    mutationFn: ({ query, lang }) => ragAPI.query(query, lang),
    onSuccess: (data) => {
      const userMessage = chatQuery
      setChatHistory((prev) => [
        ...prev,
        { type: 'user', content: userMessage, lang: chatLang },
        { type: 'assistant', content: data.answer, sources: data.sources, confidence: data.confidence },
      ])
      setChatQuery('')
    },
  })

  // Sentiment mutation
  const sentimentMutation = useMutation({
    mutationFn: (text) => mlAPI.sentiment(text),
  })

  // Tone mutation
  const toneMutation = useMutation({
    mutationFn: (text) => toneAPI.adjust(text),
  })

  // Upload mutation
  const uploadMutation = useMutation({
    mutationFn: (file) => adminAPI.embed(file),
    onSuccess: () => {
      setUploadFile(null)
      const fileInput = document.getElementById('file-input')
      if (fileInput) fileInput.value = ''
    },
  })

  const handleChatSubmit = (e) => {
    e.preventDefault()
    if (!chatQuery.trim()) return
    chatMutation.mutate({ query: chatQuery, lang: chatLang })
  }

  const handleSentimentSubmit = (e) => {
    e.preventDefault()
    if (!sentimentText.trim()) return
    sentimentMutation.mutate(sentimentText)
  }

  const handleToneSubmit = (e) => {
    e.preventDefault()
    if (!toneText.trim()) return
    toneMutation.mutate(toneText)
  }

  const handleFileChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      setUploadFile(file)
      uploadMutation.reset()
    }
  }

  const handleUploadSubmit = (e) => {
    e.preventDefault()
    if (!uploadFile) return
    uploadMutation.mutate(uploadFile)
  }

  const getSentimentColor = (label) => {
    switch (label?.toLowerCase()) {
      case 'positive': return 'bg-emerald-100 text-emerald-800 border-emerald-300'
      case 'negative': return 'bg-rose-100 text-rose-800 border-rose-300'
      case 'neutral': return 'bg-slate-100 text-slate-800 border-slate-300'
      default: return 'bg-slate-100 text-slate-800 border-slate-300'
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md border-b border-gray-200/50 sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center">
                <span className="text-white text-xl font-bold">AI</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                  AI Intelligence Platform
                </h1>
                <p className="text-xs text-gray-500">Multilingual AI Assistant</p>
              </div>
            </div>
            <nav className="hidden md:flex space-x-1">
              {[
                { id: 'chat', label: '💬 Chat', icon: '💬' },
                { id: 'sentiment', label: '😊 Sentiment', icon: '😊' },
                { id: 'tone', label: '✨ Tone', icon: '✨' },
                { id: 'upload', label: '📄 Upload', icon: '📄' },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-4 py-2 rounded-lg font-medium transition-all ${
                    activeTab === tab.id
                      ? 'bg-gradient-to-r from-indigo-500 to-purple-600 text-white shadow-lg'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Mobile Tabs */}
        <div className="md:hidden mb-6 flex space-x-2 overflow-x-auto pb-2">
          {[
            { id: 'chat', label: '💬 Chat' },
            { id: 'sentiment', label: '😊 Sentiment' },
            { id: 'tone', label: '✨ Tone' },
            { id: 'upload', label: '📄 Upload' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 rounded-lg font-medium whitespace-nowrap transition-all ${
                activeTab === tab.id
                  ? 'bg-gradient-to-r from-indigo-500 to-purple-600 text-white shadow-lg'
                  : 'bg-white text-gray-600 hover:bg-gray-50'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Chat Tab */}
        {activeTab === 'chat' && (
          <div className="bg-white/70 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 p-6 md:p-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-2">RAG Chat</h2>
            <p className="text-gray-600 mb-6">Query your documents using AI-powered retrieval</p>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">Language</label>
              <select
                value={chatLang}
                onChange={(e) => setChatLang(e.target.value)}
                className="block w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 bg-white"
              >
                <option value="en">English</option>
                <option value="hi">Hindi</option>
                <option value="es">Spanish</option>
                <option value="fr">French</option>
              </select>
            </div>

            <div className="mb-6 space-y-4 max-h-96 overflow-y-auto pr-2">
              {chatHistory.length === 0 && (
                <div className="text-center text-gray-500 py-12">
                  <div className="text-4xl mb-4">💬</div>
                  <p>Start a conversation by asking a question</p>
                </div>
              )}
              {chatHistory.map((item, idx) => (
                <div
                  key={idx}
                  className={`p-4 rounded-xl ${
                    item.type === 'user'
                      ? 'bg-gradient-to-r from-indigo-50 to-purple-50 ml-8 border border-indigo-100'
                      : 'bg-gray-50 mr-8 border border-gray-200'
                  }`}
                >
                  <div className="font-semibold mb-2 text-sm text-gray-600">
                    {item.type === 'user' ? '👤 You' : '🤖 Assistant'}
                  </div>
                  <div className="text-gray-800">{item.content}</div>
                  {item.type === 'assistant' && (
                    <div className="mt-3 pt-3 border-t border-gray-200 text-xs text-gray-600">
                      <div>Confidence: <span className="font-semibold">{(item.confidence * 100).toFixed(1)}%</span></div>
                      {item.sources && item.sources.length > 0 && (
                        <div className="mt-1">Sources: {item.sources.slice(0, 3).join(', ')}</div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>

            <form onSubmit={handleChatSubmit} className="space-y-4">
              <textarea
                value={chatQuery}
                onChange={(e) => setChatQuery(e.target.value)}
                placeholder="Ask a question about your documents..."
                rows={3}
                className="block w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 bg-white"
              />
              <button
                type="submit"
                disabled={chatMutation.isPending || !chatQuery.trim()}
                className="w-full bg-gradient-to-r from-indigo-500 to-purple-600 text-white py-3 px-6 rounded-lg font-semibold hover:from-indigo-600 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl"
              >
                {chatMutation.isPending ? '⏳ Processing...' : '🚀 Send Query'}
              </button>
              {chatMutation.isError && (
                <div className="bg-rose-50 border border-rose-200 text-rose-700 px-4 py-3 rounded-lg">
                  Error: {chatMutation.error.message}
                </div>
              )}
            </form>
          </div>
        )}

        {/* Sentiment Tab */}
        {activeTab === 'sentiment' && (
          <div className="bg-white/70 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 p-6 md:p-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-2">Sentiment Analysis</h2>
            <p className="text-gray-600 mb-6">Analyze the sentiment of any text</p>

            <form onSubmit={handleSentimentSubmit} className="space-y-4 mb-6">
              <textarea
                value={sentimentText}
                onChange={(e) => setSentimentText(e.target.value)}
                placeholder="Enter text to analyze... (e.g., 'yeh movie bohot zabardast thi!')"
                rows={6}
                className="block w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 bg-white"
              />
              <button
                type="submit"
                disabled={sentimentMutation.isPending || !sentimentText.trim()}
                className="w-full bg-gradient-to-r from-indigo-500 to-purple-600 text-white py-3 px-6 rounded-lg font-semibold hover:from-indigo-600 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl"
              >
                {sentimentMutation.isPending ? '⏳ Analyzing...' : '🔍 Analyze Sentiment'}
              </button>
              {sentimentMutation.isError && (
                <div className="bg-rose-50 border border-rose-200 text-rose-700 px-4 py-3 rounded-lg">
                  Error: {sentimentMutation.error.message}
                </div>
              )}
            </form>

            {sentimentMutation.data && (
              <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl p-6 border border-gray-200">
                <h3 className="text-xl font-semibold mb-4 text-gray-900">Results</h3>
                <div className="space-y-4">
                  <div>
                    <div className="text-sm font-medium text-gray-700 mb-2">Sentiment</div>
                    <div className={`inline-block px-6 py-3 rounded-xl border-2 font-bold text-lg ${getSentimentColor(sentimentMutation.data.label)}`}>
                      {sentimentMutation.data.label?.toUpperCase()}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-gray-700 mb-2">Confidence Score</div>
                    <div className="flex items-center space-x-4">
                      <div className="flex-1 bg-gray-200 rounded-full h-6 overflow-hidden">
                        <div
                          className="bg-gradient-to-r from-indigo-500 to-purple-600 h-6 rounded-full transition-all duration-500"
                          style={{ width: `${sentimentMutation.data.score * 100}%` }}
                        />
                      </div>
                      <span className="text-2xl font-bold text-gray-900">
                        {(sentimentMutation.data.score * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Tone Tab */}
        {activeTab === 'tone' && (
          <div className="bg-white/70 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 p-6 md:p-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-2">Tone Adjuster</h2>
            <p className="text-gray-600 mb-6">Convert text to warm, culturally South Asian conversational style</p>

            <form onSubmit={handleToneSubmit} className="space-y-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Original Text</label>
                <textarea
                  value={toneText}
                  onChange={(e) => setToneText(e.target.value)}
                  placeholder="Enter text to adjust... (e.g., 'please join the call')"
                  rows={4}
                  className="block w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 bg-white"
                />
              </div>
              <button
                type="submit"
                disabled={toneMutation.isPending || !toneText.trim()}
                className="w-full bg-gradient-to-r from-indigo-500 to-purple-600 text-white py-3 px-6 rounded-lg font-semibold hover:from-indigo-600 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl"
              >
                {toneMutation.isPending ? '⏳ Adjusting...' : '✨ Adjust Tone'}
              </button>
              {toneMutation.isError && (
                <div className="bg-rose-50 border border-rose-200 text-rose-700 px-4 py-3 rounded-lg">
                  Error: {toneMutation.error.message}
                </div>
              )}
            </form>

            {toneMutation.data && (
              <div className="space-y-4">
                <div className="bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 rounded-xl p-6 border-2 border-indigo-200">
                  <h3 className="text-xl font-semibold mb-4 text-gray-900">✨ Adjusted Text</h3>
                  <div className="text-lg text-gray-800 leading-relaxed">
                    {toneMutation.data.adjusted}
                  </div>
                </div>
                <div className="bg-gray-50 rounded-xl p-4 border border-gray-200">
                  <div className="text-sm font-medium text-gray-600 mb-1">Original:</div>
                  <div className="text-gray-500 italic">{toneText}</div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Upload Tab */}
        {activeTab === 'upload' && (
          <div className="bg-white/70 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 p-6 md:p-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-2">Document Upload</h2>
            <p className="text-gray-600 mb-6">Upload PDF, TXT, or CSV files to add them to the knowledge base</p>

            <form onSubmit={handleUploadSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Select File</label>
                <div className="mt-1 flex justify-center px-6 pt-8 pb-8 border-2 border-dashed border-gray-300 rounded-xl hover:border-indigo-400 transition-colors bg-gray-50">
                  <div className="space-y-2 text-center">
                    <div className="text-4xl mb-2">📄</div>
                    <div className="flex text-sm text-gray-600">
                      <label
                        htmlFor="file-input"
                        className="relative cursor-pointer bg-white rounded-md font-medium text-indigo-600 hover:text-indigo-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-indigo-500 px-4 py-2 rounded-lg border border-indigo-300 hover:bg-indigo-50"
                      >
                        <span>Choose a file</span>
                        <input
                          id="file-input"
                          name="file-input"
                          type="file"
                          className="sr-only"
                          accept=".pdf,.txt,.csv"
                          onChange={handleFileChange}
                        />
                      </label>
                      <p className="pl-3 pt-2">or drag and drop</p>
                    </div>
                    <p className="text-xs text-gray-500">PDF, TXT, CSV up to 10MB</p>
                    {uploadFile && (
                      <div className="mt-2 text-sm text-gray-700 bg-white px-4 py-2 rounded-lg border border-gray-200">
                        Selected: <span className="font-medium">{uploadFile.name}</span> ({(uploadFile.size / 1024).toFixed(2)} KB)
                      </div>
                    )}
                  </div>
                </div>
              </div>

              <button
                type="submit"
                disabled={uploadMutation.isPending || !uploadFile}
                className="w-full bg-gradient-to-r from-indigo-500 to-purple-600 text-white py-3 px-6 rounded-lg font-semibold hover:from-indigo-600 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl"
              >
                {uploadMutation.isPending ? '⏳ Processing...' : '📤 Upload and Embed'}
              </button>

              {uploadMutation.isError && (
                <div className="bg-rose-50 border border-rose-200 text-rose-700 px-4 py-3 rounded-lg">
                  Error: {uploadMutation.error.message}
                </div>
              )}

              {uploadMutation.data && (
                <div className="bg-gradient-to-br from-emerald-50 to-green-50 rounded-xl p-6 border-2 border-emerald-200">
                  <div className="flex items-center space-x-3 mb-4">
                    <div className="text-3xl">✅</div>
                    <h3 className="text-xl font-semibold text-emerald-900">Upload Successful!</h3>
                  </div>
                  <div className="space-y-2 text-sm">
                    <div>
                      <span className="font-medium text-emerald-800">Document ID:</span>
                      <span className="ml-2 text-emerald-700 font-mono">{uploadMutation.data.doc_id}</span>
                    </div>
                    <div>
                      <span className="font-medium text-emerald-800">Chunks Indexed:</span>
                      <span className="ml-2 text-emerald-700 font-bold text-lg">{uploadMutation.data.chunks_indexed}</span>
                    </div>
                  </div>
                  <p className="mt-4 text-sm text-emerald-700">
                    The document has been successfully processed and added to the knowledge base. You can now query it using the Chat tab.
                  </p>
                </div>
              )}
            </form>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-16 py-8 border-t border-gray-200/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-gray-600 text-sm">
          <p>AI Intelligence Platform - Powered by Groq, Qdrant, and Transformers</p>
        </div>
      </footer>
    </div>
  )
}
