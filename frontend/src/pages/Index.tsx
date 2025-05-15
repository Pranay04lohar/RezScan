import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { UploadCloud, FileText, Check } from "lucide-react";
import { toast } from "@/components/ui/sonner";
import { api, MatchResponse } from '@/lib/api';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import SkillMatchComparison from '@/components/SkillMatchComparison';

const Index = () => {
  const [similarityMetric, setSimilarityMetric] = useState<"cosine" | "euclidean" | "combined">("cosine");
  const [jobDescription, setJobDescription] = useState<File | null>(null);
  const [resumes, setResumes] = useState<File[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [results, setResults] = useState<MatchResponse | null>(null);
  const [showAllMatches, setShowAllMatches] = useState(false);

  const handleJobDescriptionChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setJobDescription(e.target.files[0]);
      toast.success("Job description uploaded successfully!");
    }
  };

  const handleResumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const fileArray = Array.from(e.target.files);
      setResumes(prevResumes => [...prevResumes, ...fileArray]);
      toast.success(`${fileArray.length} resume(s) added successfully!`);
    }
  };

  const removeResume = (index: number) => {
    setResumes(prevResumes => prevResumes.filter((_, i) => i !== index));
    toast.info("Resume removed");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!jobDescription) {
      toast.error("Please upload a job description");
      return;
    }
    
    if (resumes.length === 0) {
      toast.error("Please upload at least one resume");
      return;
    }
    
    setIsProcessing(true);
    setProgress(0);
    
    try {
      // Start progress animation
      const timer = setInterval(() => {
        setProgress(prev => {
          if (prev >= 90) {
            clearInterval(timer);
            return 90;
          }
          return prev + 10;
        });
      }, 500);

      // Call the API
      const response = await api.matchResumes(
        jobDescription,
        resumes,
        similarityMetric,
        5,
        0.3
      );

      // Clear progress timer and set to 100%
      clearInterval(timer);
      setProgress(100);
      
      // Update results
      setResults(response);
      toast.success("Analysis complete!");
    } catch (error: any) {
      console.error('Error:', error);
      // Show more detailed error message
      const errorMessage = error.response?.data?.error || error.message || "An error occurred during processing";
      toast.error(errorMessage);
    } finally {
      setIsProcessing(false);
    }
  };

  const resetForm = () => {
    setSimilarityMetric("cosine");
    setJobDescription(null);
    setResumes([]);
    setResults(null);
    setProgress(0);
    setShowAllMatches(false);
    toast.info("Form reset");
  };

  // Helper to get file name from resume_id
  const getResumeFileName = (resume_id) => {
    const idx = parseInt(resume_id.replace('resume_', ''), 10);
    return resumes[idx]?.name || resume_id;
  };

  // Determine which matches to show
  const matchesToShow = results
    ? (showAllMatches ? results.matches : results.matches.slice(0, 5))
    : [];

  const handleDownloadPDF = () => {
    const doc = new jsPDF();
    doc.text('Detailed Match Table', 14, 16);

    // Prepare table data
    const tableColumn = ["Rank", "Resume Name", "Cosine Similarity", "Euclidean Score", "Match %"];
    const tableRows = results.matches.map((match) => [
      match.rank,
      getResumeFileName(match.resume_id),
      (match.explanation.cosine_similarity * 100).toFixed(1) + '%',
      (match.explanation.euclidean_similarity * 100).toFixed(1) + '%',
      (((match.explanation.cosine_similarity + match.explanation.euclidean_similarity) / 2) * 100).toFixed(1) + '%'
    ]);

    autoTable(doc, {
      head: [tableColumn],
      body: tableRows,
      startY: 22,
    });

    doc.save('detailed_match_table.pdf');
  };

  return (
    <div className="min-h-screen bg-gray-100 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-blue-600">RezScan</h1>
          <p className="mt-2 text-lg text-gray-600">Upload job descriptions and resumes to find the best match</p>
        </div>
        
        {!results ? (
          <Card className="shadow-lg">
            <CardHeader>
              <CardTitle>Resume Matching</CardTitle>
              <CardDescription>
                Upload a job description and candidate resumes to find the best matches using BERT-based semantic matching
              </CardDescription>
            </CardHeader>
            
            <form onSubmit={handleSubmit}>
              <CardContent className="space-y-6">
                {/* Similarity Metric Selection */}
                {/* <div className="space-y-3">
                  <h3 className="font-medium text-lg">Select Similarity Metric</h3>
                  <RadioGroup value={similarityMetric} onValueChange={(value) => setSimilarityMetric(value as "cosine" | "euclidean" | "combined")} className="flex flex-col sm:flex-row gap-4">
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="cosine" id="cosine" />
                      <Label htmlFor="cosine">Cosine Similarity</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="euclidean" id="euclidean" />
                      <Label htmlFor="euclidean">Euclidean Similarity</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="combined" id="combined" />
                      <Label htmlFor="combined">Combined</Label>
                    </div>
                  </RadioGroup>
                </div> */}
                
                {/* Job Description Upload */}
                <div className="space-y-3">
                  <h3 className="font-medium text-lg">Job Description</h3>
                  <div className="border-2 border-dashed rounded-lg p-6 text-center">
                    {jobDescription ? (
                      <div className="flex items-center justify-between bg-blue-50 p-3 rounded">
                        <div className="flex items-center space-x-2">
                          <FileText className="h-5 w-5 text-blue-500" />
                          <span>{jobDescription.name}</span>
                        </div>
                        <Button 
                          variant="ghost" 
                          size="sm" 
                          onClick={() => setJobDescription(null)}
                          className="h-8 text-red-500 hover:text-red-700"
                        >
                          Remove
                        </Button>
                      </div>
                    ) : (
                      <div>
                        <UploadCloud className="h-10 w-10 text-gray-400 mx-auto mb-3" />
                        <Label 
                          htmlFor="job-description" 
                          className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded cursor-pointer inline-block"
                        >
                          Upload Job Description
                        </Label>
                        <p className="mt-2 text-sm text-gray-500">Supports PDF or DOCX files</p>
                      </div>
                    )}
                    <Input
                      id="job-description"
                      type="file"
                      accept=".pdf,.docx"
                      onChange={handleJobDescriptionChange}
                      className="hidden"
                    />
                  </div>
                </div>
                
                {/* Resume Upload */}
                <div className="space-y-3">
                  <h3 className="font-medium text-lg">Resumes</h3>
                  <div className="border-2 border-dashed rounded-lg p-6 text-center">
                    <div>
                      <UploadCloud className="h-10 w-10 text-gray-400 mx-auto mb-3" />
                      <Label 
                        htmlFor="resumes" 
                        className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded cursor-pointer inline-block"
                      >
                        Upload Resumes
                      </Label>
                      <p className="mt-2 text-sm text-gray-500">You can select multiple files</p>
                    </div>
                    <Input
                      id="resumes"
                      type="file"
                      multiple
                      accept=".pdf,.docx"
                      onChange={handleResumeChange}
                      className="hidden"
                    />
                  </div>
                </div>
                
                {/* Resume List */}
                {resumes.length > 0 && (
                  <div className="space-y-2">
                    <h3 className="font-medium">Uploaded Resumes ({resumes.length})</h3>
                    <div className="space-y-2 max-h-40 overflow-y-auto">
                      {resumes.map((resume, index) => (
                        <div key={index} className="flex items-center justify-between bg-gray-50 p-2 rounded">
                          <div className="flex items-center space-x-2">
                            <FileText className="h-4 w-4 text-gray-500" />
                            <span className="text-sm truncate max-w-[250px]">{resume.name}</span>
                          </div>
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            onClick={() => removeResume(index)}
                            className="h-6 text-red-500 hover:text-red-700"
                          >
                            Remove
                          </Button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* Progress Bar */}
                {isProcessing && (
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm text-gray-600">
                      <span>Processing...</span>
                      <span>{progress}%</span>
                    </div>
                    <Progress value={progress} className="h-2" />
                  </div>
                )}
              </CardContent>
              
              <CardFooter className="flex justify-between">
                <Button
                  type="button"
                  variant="outline"
                  onClick={resetForm}
                  disabled={isProcessing}
                >
                  Reset
                </Button>
                <Button
                  type="submit"
                  disabled={isProcessing || !jobDescription || resumes.length === 0}
                >
                  {isProcessing ? "Processing..." : "Analyze"}
                </Button>
              </CardFooter>
            </form>
          </Card>
        ) : (
          <div className="space-y-6">
            {/* Results Header */}
            <Card>
              <CardHeader>
                <CardTitle>Analysis Results</CardTitle>
                <CardDescription>
                  {results.message}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <h3 className="font-medium text-blue-700">Total Resumes</h3>
                    <p className="text-2xl font-bold text-blue-600">{results.ranking_summary.total_matches}</p>
                  </div>
                  <div className="bg-green-50 p-4 rounded-lg">
                    <h3 className="font-medium text-green-700">Average Score</h3>
                    <p className="text-2xl font-bold text-green-600">
                      {(results.ranking_summary.average_score * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div className="bg-purple-50 p-4 rounded-lg">
                    <h3 className="font-medium text-purple-700">Score Distribution</h3>
                    <div className="space-y-1">
                      <div className="flex justify-between">
                        <span className="text-sm">High</span>
                        <span className="text-sm font-medium">{results.ranking_summary.score_distribution.high}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm">Medium</span>
                        <span className="text-sm font-medium">{results.ranking_summary.score_distribution.medium}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm">Low</span>
                        <span className="text-sm font-medium">{results.ranking_summary.score_distribution.low}</span>
                    </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Matches Table */}
            <Card>
              <CardHeader>
                <CardTitle>Detailed Match Table</CardTitle>
                <CardDescription>
                  Showing {showAllMatches ? 'all' : 'top 5'} matches based on {results.similarity_metric} similarity
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button
                  variant="outline"
                  className="mb-4 bg-green-500 hover:bg-green-600 text-white"
                  onClick={handleDownloadPDF}
                >
                  Download PDF Report
                </Button>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Rank</TableHead>
                      <TableHead>Resume Name</TableHead>
                      <TableHead>Cosine Similarity</TableHead>
                      <TableHead>Euclidean Score</TableHead>
                      <TableHead>Match %</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                    {matchesToShow.map((match) => {
                      const cosine = match.explanation.cosine_similarity;
                      const euclidean = match.explanation.euclidean_similarity;
                      const avgMatch = (cosine + euclidean) / 2;
                      return (
                        <TableRow key={match.resume_id}>
                          <TableCell>{match.rank}</TableCell>
                          <TableCell>{getResumeFileName(match.resume_id)}</TableCell>
                          <TableCell>
                            {(cosine * 100).toFixed(1)}%
                          </TableCell>
                          <TableCell>
                            {(euclidean * 100).toFixed(1)}%
                          </TableCell>
                          <TableCell>
                            {(avgMatch * 100).toFixed(1)}%
                          </TableCell>
                        </TableRow>
                      );
                    })}
                    </TableBody>
                  </Table>
                {results.matches.length > 5 && (
                  <div className="flex justify-center mt-4">
                    <Button
                      variant="outline"
                      onClick={() => setShowAllMatches((prev) => !prev)}
                    >
                      {showAllMatches ? 'Show Top 5' : 'Show All Matches'}
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Replace individual skill visualizations with combined comparison */}
            <SkillMatchComparison
              matches={results.matches.map(match => ({
                resume_id: match.resume_id,
                resume_name: getResumeFileName(match.resume_id),
                skill_match: match.skill_match
              }))}
            />

            {/* Action Buttons */}
            <div className="flex justify-center space-x-4">
              <Button
                variant="outline"
                onClick={resetForm}
              >
                Start New Analysis
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Index;
