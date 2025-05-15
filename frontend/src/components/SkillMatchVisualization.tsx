import React from 'react';
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from 'chart.js';
import { Radar } from 'react-chartjs-2';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
);

interface SkillMatchVisualizationProps {
  jobDescriptionSkills: string[];
  resumeSkills: string[];
  resumeName: string;
}

const SkillMatchVisualization: React.FC<SkillMatchVisualizationProps> = ({
  jobDescriptionSkills = [],
  resumeSkills = [],
  resumeName,
}) => {
  // If no skills are available, show a message
  if (jobDescriptionSkills.length === 0 && resumeSkills.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Skill Match Analysis - {resumeName}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center text-gray-500 py-8">
            No skills data available for comparison
          </div>
        </CardContent>
      </Card>
    );
  }

  // Combine all unique skills
  const allSkills = Array.from(new Set([...jobDescriptionSkills, ...resumeSkills]));

  // If there are no skills to display, return early
  if (allSkills.length === 0) {
    return null;
  }

  // Calculate skill match scores
  const jobDescriptionScores = allSkills.map(skill => 
    jobDescriptionSkills.includes(skill) ? 1 : 0
  );
  
  const resumeScores = allSkills.map(skill => 
    resumeSkills.includes(skill) ? 1 : 0
  );

  const data = {
    labels: allSkills,
    datasets: [
      {
        label: 'Job Description',
        data: jobDescriptionScores,
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1,
      },
      {
        label: resumeName,
        data: resumeScores,
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
        borderColor: 'rgba(255, 99, 132, 1)',
        borderWidth: 1,
      },
    ],
  };

  const options = {
    scales: {
      r: {
        beginAtZero: true,
        max: 1,
        ticks: {
          stepSize: 1,
        },
      },
    },
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Skill Match Analysis',
      },
    },
  };

  // Calculate missing skills
  const missingSkills = jobDescriptionSkills.filter(
    skill => !resumeSkills.includes(skill)
  );

  return (
    <Card>
      <CardHeader>
        <CardTitle>Skill Match Analysis - {resumeName}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[400px]">
          <Radar data={data} options={options} />
        </div>
        {missingSkills.length > 0 && (
          <div className="mt-4 p-4 bg-red-50 rounded-lg">
            <h3 className="font-medium text-red-700 mb-2">Missing Skills:</h3>
            <ul className="list-disc list-inside text-red-600">
              {missingSkills.map((skill, index) => (
                <li key={index}>{skill}</li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default SkillMatchVisualization; 