"use client"

import { useState } from "react"
import { ReportUploader } from "@/components/report-uploader"
import { Dashboard } from "@/components/dashboard"
import type { ReportData } from "@/lib/types"

export default function Home() {
  const [reportData, setReportData] = useState<ReportData | null>(null)

  return (
    <main className="min-h-screen bg-background">
      {!reportData ? (
        <ReportUploader onDataLoaded={setReportData} />
      ) : (
        <Dashboard data={reportData} onReset={() => setReportData(null)} />
      )}
    </main>
  )
}
