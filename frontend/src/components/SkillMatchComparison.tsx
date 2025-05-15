import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface SkillMatchComparisonProps {
  matches: Array<{
    resume_id: string;
    resume_name: string;
    skill_match?: {
      match_percentage: number;
      job_description_skills: string[];
      resume_skills: string[];
      matching_skills?: string[];
      missing_skills?: string[];
    };
  }>;
}

const SkillMatchComparison: React.FC<SkillMatchComparisonProps> = ({ matches }) => {
  const validMatches = matches.filter((m) => m.skill_match);
  if (validMatches.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Skill Match Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center text-gray-500 py-8">
            No skill match data available for analysis
          </div>
        </CardContent>
      </Card>
    );
  }

  // Get all unique required skills from job description
  const allSkills = Array.from(
    new Set(validMatches[0]?.skill_match?.job_description_skills || [])
  );

  return (
    <Card>
      <CardHeader>
        <CardTitle>Skill Match Heatmap</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="min-w-full border text-center">
            <thead>
              <tr>
                <th className="border px-2 py-1 bg-gray-100">Resume</th>
                {allSkills.map((skill) => (
                  <th key={skill} className="border px-2 py-1 bg-gray-100 text-xs">
                    {skill}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {validMatches.map((match) => (
                <tr key={match.resume_id}>
                  <td className="border px-2 py-1 font-medium bg-gray-50">{match.resume_name}</td>
                  {allSkills.map((skill) => {
                    const hasSkill = match.skill_match?.resume_skills?.includes(skill);
                    return (
                      <td
                        key={skill}
                        className={`border px-2 py-1 ${hasSkill ? "bg-green-200" : "bg-red-200"}`}
                        title={hasSkill ? "Present" : "Missing"}
                      >
                        {hasSkill ? "✓" : "✗"}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
};

export default SkillMatchComparison; 