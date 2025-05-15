import os
import tempfile
from typing import List, Tuple
from werkzeug.datastructures import FileStorage
import shutil

class FileHandler:
    def __init__(self, upload_folder: str):
        self.upload_folder = upload_folder
        self.temp_dir = None

    def create_temp_directory(self) -> str:
        """Create a temporary directory for processing files."""
        self.temp_dir = tempfile.mkdtemp(dir=self.upload_folder)
        return self.temp_dir

    def save_files(self, job_description: FileStorage, resumes: List[FileStorage]) -> Tuple[str, List[str]]:
        """
        Save uploaded files to temporary directory.
        Returns paths to saved job description and resume files.
        """
        if not self.temp_dir:
            self.create_temp_directory()

        # Save job description
        jd_filename = f'job_description.{job_description.filename.split(".")[-1]}'
        jd_path = os.path.join(self.temp_dir, jd_filename)
        job_description.save(jd_path)

        # Save resumes
        resume_paths = []
        for i, resume in enumerate(resumes):
            filename = f'resume_{i}.{resume.filename.split(".")[-1]}'
            resume_path = os.path.join(self.temp_dir, filename)
            resume.save(resume_path)
            resume_paths.append(resume_path)

        return jd_path, resume_paths

    def cleanup(self):
        """Remove temporary directory and its contents."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            self.temp_dir = None

    def cleanup_files(self, jd_path, resume_paths):
        try:
            if os.path.exists(jd_path):
                os.remove(jd_path)
            for path in resume_paths:
                if os.path.exists(path):
                    os.remove(path)
        except Exception as e:
            print(f"Error cleaning up files: {e}")

    def __del__(self):
        """Ensure cleanup on object destruction."""
        self.cleanup() 