import './globals.css'
import { Inter } from 'next/font/google'
import { Providers } from './providers'
import { ErrorBoundary } from './error-boundary'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'AI Intelligence Platform',
  description: 'AI-powered platform with RAG, sentiment analysis, and tone adjustment',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className} suppressHydrationWarning>
        <ErrorBoundary>
          <Providers>
            {children}
          </Providers>
        </ErrorBoundary>
      </body>
    </html>
  )
}

