from clientsService import celery_app
import os
from resume_analysis.database import save_resume_analysis_sync, SaveResumeAnalysis
from resume_analysis.langchain_test import ResumeAnalyzer
from resume_analysis.document_process import extract_text_from_pdf, extract_text_from_word
import asyncio
from typing import Dict


@celery_app.task(name='tasks.full_resume_analysis')
def full_resume_analysis(resume_file_path: str, job_description: str):

    
    # Extract text from file based on extension
    try:
        file_extension = os.path.splitext(resume_file_path)[1].lower()
        
        # Create an async function to call the async extraction functions
        async def extract_text():
            if file_extension == ".pdf":
                return await extract_text_from_pdf(resume_file_path)
            elif file_extension in [".docx", ".doc"]:
                return await extract_text_from_word(resume_file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
        
        # Run the async function in a new event loop
        resume_text = asyncio.run(extract_text())
        
        # Perform analysis
        analyzer = ResumeAnalyzer()
        result = analyzer.get_missing_keywords(resume_text, job_description)
        

        # Create a SaveResumeAnalysis Pydantic object
        resume_data = SaveResumeAnalysis(
            task_id=full_resume_analysis.request.id,
            resume_text=resume_text,
            job_description=job_description,
            analysis_results=result
        )

        # Pass the object to the sync function
        save_resume_analysis_sync(resume_data)
            
        return {
            "analysis": result,
            "task_id": full_resume_analysis.request.id
        }
        
    except Exception as e:
        # Return error information
        return {
            "status": "error",
            "error_type": type(e).__name__,
            "error_message": str(e)
        }
    finally:
        # Clean up the file after processing
        try:
            if os.path.exists(resume_file_path):
                os.remove(resume_file_path)
        except Exception as cleanup_error:
            print(f"Error removing temporary file {resume_file_path}: {str(cleanup_error)}")
        
@celery_app.task(name='tasks.full_resume_analysis')
def full_resume_analysis(resume_file_path: str, job_description: str):
    try:
        file_extension = os.path.splitext(resume_file_path)[1].lower()

        async def extract_text():
            if file_extension == ".pdf":
                return await extract_text_from_pdf(resume_file_path)
            elif file_extension in [".docx", ".doc"]:
                return await extract_text_from_word(resume_file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")

        # Run the async extraction
        resume_text = asyncio.run(extract_text())

        # Perform analysis
        analyzer = ResumeAnalyzer()
        analysis_result = analyzer.get_missing_keywords(resume_text, job_description)

        # Create the data object
        resume_data = SaveResumeAnalysis(
            task_id=full_resume_analysis.request.id,
            resume_text=resume_text,
            job_description=job_description,
            analysis_results=analysis_result
        )

        # Save the analysis results
        save_resume_analysis_sync(resume_data)

        return {
            "status": "success",
            "analysis": analysis_result,
            "task_id": full_resume_analysis.request.id
        }

    except Exception as e:
        # Log error or take appropriate action
        return {
            "status": "error",
            "message": str(e),
            "task_id": full_resume_analysis.request.id
        }


@celery_app.task(name='tasks.generate_resume_with_keyword')
def generate_resume_with_keyword(resume_file_path: str, missing_keywords: str):
    from resume_analysis.langchain_test import ResumeAnalyzer
    from resume_analysis.document_process import extract_text_from_pdf, extract_text_from_word, generate_resume_from_json
    import asyncio

    # Extract text from file based on extension
    try:
        file_extension = os.path.splitext(resume_file_path)[1].lower()
        
        # Create an async function to call the async extraction functions
        async def extract_text():
            if file_extension == ".pdf":
                return await extract_text_from_pdf(resume_file_path)
            elif file_extension in [".docx", ".doc"]:
                return await extract_text_from_word(resume_file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
        
        # Run the async function in a new event loop
        resume_text = asyncio.run(extract_text())
        
        # Perform analysis
        analyzer = ResumeAnalyzer()
        result = analyzer.get_structured_resume_from_keywords(resume_text, missing_keywords)

        pdf_result = asyncio.run(generate_resume_from_json(result))
    
        if pdf_result:
            return {
                "pdf": {
                    "filename": pdf_result["filename"],
                    "pdf_path": pdf_result["pdf_path"],
                    "download_url": pdf_result["download_url"]
                }
            }
        else:
            return {
                "status": "error",
                "result": result,
                "error_message": "Failed to generate PDF resume"
            }
    except Exception as e:
        # Return error information
        return {
            "status": "error",
            "error_type": type(e).__name__,
            "error_message": str(e)
        }
    finally:
        # Clean up the file after processing
        try:
            if os.path.exists(resume_file_path):
                os.remove(resume_file_path)
        except Exception as cleanup_error:
            print(f"Error removing temporary file {resume_file_path}: {str(cleanup_error)}")
