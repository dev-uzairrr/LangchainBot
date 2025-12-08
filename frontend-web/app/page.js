'use client'

import { useState, useEffect } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { ragAPI, mlAPI, toneAPI, adminAPI } from '@/lib/api'

export default function Home() {
  const [activeTab, setActiveTab] = useState('chat')
  const [chatQuery, setChatQuery] = useState('')
  const [chatLang, setChatLang] = useState('en')
  const [chatHistory, setChatHistory] = useState([])
  const [sentimentText, setSentimentText] = useState('')
  const [toneText, setToneText] = useState('')
  const [uploadFile, setUploadFile] = useState(null)

  // Check if documents exist
  const { data: statsData, refetch: refetchStats } = useQuery({
    queryKey: ['collectionStats'],
    queryFn: () => adminAPI.stats(),
    refetchInterval: 5000, // Refetch every 5 seconds
  })

  const hasDocuments = statsData?.has_documents || false

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
      // Refetch stats after successful upload
      refetchStats()
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
      case 'positive': return 'bg-emerald-50 text-emerald-700 border-emerald-200'
      case 'negative': return 'bg-red-50 text-red-700 border-red-200'
      case 'neutral': return 'bg-slate-50 text-slate-700 border-slate-200'
      default: return 'bg-slate-50 text-slate-700 border-slate-200'
    }
  }

  const tabs = [
    { id: 'chat', label: 'Chat', icon: '💬' },
    { id: 'sentiment', label: 'Sentiment', icon: '😊' },
    { id: 'tone', label: 'Tone', icon: '✨' },
    { id: 'upload', label: 'Upload', icon: '📄' },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100">
      {/* Header */}
      <header className="bg-white border-b border-slate-200/80 sticky top-0 z-50 shadow-sm backdrop-blur-lg bg-white/95">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-lg flex items-center justify-center shadow-md">
                <span className="text-white text-lg font-bold">AI</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-slate-900">AI Intelligence Platform</h1>
                <p className="text-xs text-slate-500 font-medium">Multilingual AI Assistant</p>
              </div>
            </div>
            <nav className="hidden md:flex space-x-1">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-5 py-2.5 rounded-lg font-medium text-sm transition-all duration-200 ${
                    activeTab === tab.id
                      ? 'bg-indigo-600 text-white shadow-md shadow-indigo-200'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
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
      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Mobile Tabs */}
        <div className="md:hidden mb-6 flex space-x-2 overflow-x-auto pb-2 scrollbar-hide">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2.5 rounded-lg font-medium text-sm whitespace-nowrap transition-all ${
                activeTab === tab.id
                  ? 'bg-indigo-600 text-white shadow-md'
                  : 'bg-white text-slate-600 hover:bg-slate-50 border border-slate-200'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Chat Tab */}
        {activeTab === 'chat' && (
          <div className="bg-white rounded-xl shadow-lg border border-slate-200 overflow-hidden">
            <div className="bg-gradient-to-r from-indigo-600 to-purple-600 px-6 py-5">
              <h2 className="text-2xl font-bold text-white">Document Chat</h2>
              <p className="text-indigo-100 text-sm mt-1">Query your documents using AI-powered retrieval</p>
            </div>
            
            <div className="p-6 space-y-6">
              {!hasDocuments && (
                <div className="bg-amber-50 border-l-4 border-amber-400 rounded-r-lg p-5">
                  <div className="flex items-start">
                    <div className="flex-shrink-0">
                      <svg className="h-6 w-6 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                      </svg>
                    </div>
                    <div className="ml-4 flex-1">
                      <h3 className="text-lg font-semibold text-amber-900 mb-1">No Documents Found</h3>
                      <p className="text-amber-800 text-sm mb-4">
                        Please upload documents using the Upload tab before you can start chatting.
                      </p>
                      <button
                        onClick={() => setActiveTab('upload')}
                        className="inline-flex items-center px-4 py-2 bg-amber-600 text-white text-sm font-medium rounded-lg hover:bg-amber-700 transition-colors shadow-sm"
                      >
                        Go to Upload
                        <svg className="ml-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
              )}
              
              {hasDocuments && statsData && (
                <div className="bg-indigo-50 border border-indigo-200 rounded-lg px-4 py-3 flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <svg className="h-5 w-5 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                    </svg>
                    <span className="text-sm font-medium text-indigo-900">Knowledge Base</span>
                  </div>
                  <span className="text-sm font-semibold text-indigo-700">{statsData.total_chunks} chunks indexed</span>
                </div>
              )}

              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">Language</label>
                <select
                  value={chatLang}
                  onChange={(e) => setChatLang(e.target.value)}
                  className="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white text-slate-900 text-sm font-medium"
                >
                  <option value="en">English</option>
                  <option value="hi">Hindi</option>
                  <option value="es">Spanish</option>
                  <option value="fr">French</option>
                </select>
              </div>

              <div className="bg-slate-50 rounded-lg border border-slate-200 p-4 max-h-96 overflow-y-auto">
                {chatHistory.length === 0 && (
                  <div className="text-center py-12">
                    <svg className="mx-auto h-12 w-12 text-slate-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                    </svg>
                    <p className="text-slate-500 font-medium">Start a conversation by asking a question</p>
                  </div>
                )}
                <div className="space-y-4">
                  {chatHistory.map((item, idx) => (
                    <div
                      key={idx}
                      className={`flex ${item.type === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[80%] rounded-lg px-4 py-3 ${
                          item.type === 'user'
                            ? 'bg-indigo-600 text-white'
                            : 'bg-white border border-slate-200 text-slate-900'
                        }`}
                      >
                        <div className="text-sm font-semibold mb-1.5 opacity-80">
                          {item.type === 'user' ? 'You' : 'Assistant'}
                        </div>
                        <div className="text-sm leading-relaxed whitespace-pre-wrap">{item.content}</div>
                        {item.type === 'assistant' && (
                          <div className="mt-3 pt-3 border-t border-slate-200 text-xs text-slate-500 space-y-1">
                            <div>
                              <span className="font-medium">Confidence:</span>{' '}
                              <span className="font-semibold text-slate-700">{(item.confidence * 100).toFixed(1)}%</span>
                            </div>
                            {item.sources && item.sources.length > 0 && (
                              <div>
                                <span className="font-medium">Sources:</span>{' '}
                                <span className="text-slate-600">{item.sources.slice(0, 3).join(', ')}</span>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <form onSubmit={handleChatSubmit} className="space-y-4">
                <div>
                  <textarea
                    value={chatQuery}
                    onChange={(e) => setChatQuery(e.target.value)}
                    placeholder={hasDocuments ? "Ask a question about your documents..." : "Upload documents first to enable chat..."}
                    rows={4}
                    disabled={!hasDocuments}
                    className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white text-slate-900 placeholder-slate-400 disabled:bg-slate-50 disabled:cursor-not-allowed resize-none"
                  />
                </div>
                <button
                  type="submit"
                  disabled={chatMutation.isPending || !chatQuery.trim() || !hasDocuments}
                  className="w-full bg-indigo-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md hover:shadow-lg"
                >
                  {chatMutation.isPending ? 'Processing...' : hasDocuments ? 'Send Query' : 'Upload Documents First'}
                </button>
                {chatMutation.isError && (
                  <div className="bg-red-50 border-l-4 border-red-400 rounded-r-lg p-4">
                    <div className="flex">
                      <div className="flex-shrink-0">
                        <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                        </svg>
                      </div>
                      <div className="ml-3">
                        <p className="text-sm text-red-700 font-medium">Error: {chatMutation.error.message}</p>
                      </div>
                    </div>
                  </div>
                )}
              </form>
            </div>
          </div>
        )}

        {/* Sentiment Tab */}
        {activeTab === 'sentiment' && (
          <div className="bg-white rounded-xl shadow-lg border border-slate-200 overflow-hidden">
            <div className="bg-gradient-to-r from-indigo-600 to-purple-600 px-6 py-5">
              <h2 className="text-2xl font-bold text-white">Sentiment Analysis</h2>
              <p className="text-indigo-100 text-sm mt-1">Analyze the sentiment of any text</p>
            </div>

            <div className="p-6 space-y-6">
              <form onSubmit={handleSentimentSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-2">Text to Analyze</label>
                  <textarea
                    value={sentimentText}
                    onChange={(e) => setSentimentText(e.target.value)}
                    placeholder="Enter text to analyze sentiment..."
                    rows={6}
                    className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white text-slate-900 placeholder-slate-400 resize-none"
                  />
                </div>
                <button
                  type="submit"
                  disabled={sentimentMutation.isPending || !sentimentText.trim()}
                  className="w-full bg-indigo-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md hover:shadow-lg"
                >
                  {sentimentMutation.isPending ? 'Analyzing...' : 'Analyze Sentiment'}
                </button>
                {sentimentMutation.isError && (
                  <div className="bg-red-50 border-l-4 border-red-400 rounded-r-lg p-4">
                    <p className="text-sm text-red-700 font-medium">Error: {sentimentMutation.error.message}</p>
                  </div>
                )}
              </form>

              {sentimentMutation.data && (
                <div className="bg-slate-50 rounded-lg border border-slate-200 p-6">
                  <h3 className="text-lg font-bold text-slate-900 mb-6">Analysis Results</h3>
                  <div className="space-y-6">
                    <div>
                      <div className="text-sm font-semibold text-slate-700 mb-3">Sentiment</div>
                      <div className={`inline-flex items-center px-6 py-3 rounded-lg border-2 font-bold text-base ${getSentimentColor(sentimentMutation.data.label)}`}>
                        {sentimentMutation.data.label?.toUpperCase()}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm font-semibold text-slate-700 mb-3">Confidence Score</div>
                      <div className="flex items-center space-x-4">
                        <div className="flex-1 bg-slate-200 rounded-full h-3 overflow-hidden">
                          <div
                            className="bg-gradient-to-r from-indigo-600 to-purple-600 h-3 rounded-full transition-all duration-500"
                            style={{ width: `${sentimentMutation.data.score * 100}%` }}
                          />
                        </div>
                        <span className="text-xl font-bold text-slate-900 min-w-[60px] text-right">
                          {(sentimentMutation.data.score * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Tone Tab */}
        {activeTab === 'tone' && (
          <div className="bg-white rounded-xl shadow-lg border border-slate-200 overflow-hidden">
            <div className="bg-gradient-to-r from-indigo-600 to-purple-600 px-6 py-5">
              <h2 className="text-2xl font-bold text-white">Tone Adjuster</h2>
              <p className="text-indigo-100 text-sm mt-1">Convert text to warm, culturally South Asian conversational style</p>
            </div>

            <div className="p-6 space-y-6">
              <form onSubmit={handleToneSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-2">Original Text</label>
                  <textarea
                    value={toneText}
                    onChange={(e) => setToneText(e.target.value)}
                    placeholder="Enter text to adjust tone..."
                    rows={5}
                    className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white text-slate-900 placeholder-slate-400 resize-none"
                  />
                </div>
                <button
                  type="submit"
                  disabled={toneMutation.isPending || !toneText.trim()}
                  className="w-full bg-indigo-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md hover:shadow-lg"
                >
                  {toneMutation.isPending ? 'Adjusting...' : 'Adjust Tone'}
                </button>
                {toneMutation.isError && (
                  <div className="bg-red-50 border-l-4 border-red-400 rounded-r-lg p-4">
                    <p className="text-sm text-red-700 font-medium">Error: {toneMutation.error.message}</p>
                  </div>
                )}
              </form>

              {toneMutation.data && (
                <div className="space-y-4">
                  <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-lg border-2 border-indigo-200 p-6">
                    <h3 className="text-lg font-bold text-slate-900 mb-4">Adjusted Text</h3>
                    <div className="text-slate-800 leading-relaxed whitespace-pre-wrap">
                      {toneMutation.data.adjusted}
                    </div>
                  </div>
                  <div className="bg-slate-50 rounded-lg border border-slate-200 p-4">
                    <div className="text-sm font-semibold text-slate-600 mb-2">Original Text</div>
                    <div className="text-slate-600 italic whitespace-pre-wrap">{toneText}</div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Upload Tab */}
        {activeTab === 'upload' && (
          <div className="bg-white rounded-xl shadow-lg border border-slate-200 overflow-hidden">
            <div className="bg-gradient-to-r from-indigo-600 to-purple-600 px-6 py-5">
              <h2 className="text-2xl font-bold text-white">Document Upload</h2>
              <p className="text-indigo-100 text-sm mt-1">Upload PDF, TXT, or CSV files to add them to the knowledge base</p>
            </div>

            <div className="p-6">
              <form onSubmit={handleUploadSubmit} className="space-y-6">
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-3">Select File</label>
                  <div className="mt-1 flex justify-center px-6 pt-12 pb-12 border-2 border-dashed border-slate-300 rounded-lg hover:border-indigo-400 transition-colors bg-slate-50">
                    <div className="text-center">
                      <svg className="mx-auto h-12 w-12 text-slate-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                      </svg>
                      <div className="flex items-center justify-center space-x-2 text-sm text-slate-600">
                        <label
                          htmlFor="file-input"
                          className="relative cursor-pointer bg-white rounded-md font-medium text-indigo-600 hover:text-indigo-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-indigo-500 px-4 py-2 border border-indigo-300 hover:bg-indigo-50 transition-colors"
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
                        <span className="text-slate-400">or drag and drop</span>
                      </div>
                      <p className="mt-2 text-xs text-slate-500">PDF, TXT, CSV up to 10MB</p>
                      {uploadFile && (
                        <div className="mt-4 inline-flex items-center px-4 py-2 bg-white border border-slate-200 rounded-lg text-sm text-slate-700">
                          <svg className="h-5 w-5 text-slate-400 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                          <span className="font-medium">{uploadFile.name}</span>
                          <span className="ml-2 text-slate-500">({(uploadFile.size / 1024).toFixed(2)} KB)</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={uploadMutation.isPending || !uploadFile}
                  className="w-full bg-indigo-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md hover:shadow-lg"
                >
                  {uploadMutation.isPending ? 'Processing...' : 'Upload and Embed'}
                </button>

                {uploadMutation.isError && (
                  <div className="bg-red-50 border-l-4 border-red-400 rounded-r-lg p-4">
                    <p className="text-sm text-red-700 font-medium">Error: {uploadMutation.error.message}</p>
                  </div>
                )}

                {uploadMutation.data && (
                  <div className="bg-emerald-50 border-l-4 border-emerald-400 rounded-r-lg p-5">
                    <div className="flex items-start">
                      <div className="flex-shrink-0">
                        <svg className="h-6 w-6 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      </div>
                      <div className="ml-4 flex-1">
                        <h3 className="text-lg font-semibold text-emerald-900 mb-3">Upload Successful</h3>
                        <div className="space-y-2 text-sm">
                          <div className="flex items-center space-x-2">
                            <span className="font-medium text-emerald-800">Document ID:</span>
                            <span className="text-emerald-700 font-mono text-xs">{uploadMutation.data.doc_id}</span>
                          </div>
                          <div className="flex items-center space-x-2">
                            <span className="font-medium text-emerald-800">Chunks Indexed:</span>
                            <span className="text-emerald-700 font-bold text-base">{uploadMutation.data.chunks_indexed}</span>
                          </div>
                        </div>
                        <p className="mt-4 text-sm text-emerald-700">
                          The document has been successfully processed and added to the knowledge base. You can now query it using the Chat tab.
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </form>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-16 py-8 border-t border-slate-200 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-slate-600 text-sm font-medium">AI Intelligence Platform - Powered by Groq, Qdrant, and Transformers</p>
        </div>
      </footer>
    </div>
  )
}
