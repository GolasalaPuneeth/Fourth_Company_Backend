base_Asserts = [
    {
        'id': 1,
        'full_name': "Aravind Rokkam",
        'designation': "Software Engineer at Picarro",
        'comment': "I can't thank HasTech Info enough for helping me land my Software Engineer role at Picarro. The support and guidance I received really made all the difference in preparing me for this opportunity.",
        'image_url': "/static/base_Asserts_images/" 
    },

    {
        'id': 2,
        'full_name': "Surya Mantena",
        'designation': "Senior Analyst - Data Solutions at Comcast Corporation",
        'comment': "I'm beyond excited to join Comcast as a Senior Analyst in Data Solutions, and it's all thanks to HasTech Info! The practical training and job placement assistance were key in helping me get to where I am today.",
        'image_url': "/static/base_Asserts_images/"
    },
    {
        'id': 3,
        'full_name': "Ritvik Reddy Kandanelly",
        'designation': "Data Engineer at NYU Health",
        'comment': "HasTech Info played a huge role in my journey to becoming a Data Engineer at NYU Health. The hands-on training and interview prep were incredibly helpful in securing this job.",
        'image_url': "/static/base_Asserts_images/"
    },
    {
        'id': 4,
        'full_name': "Satya Sri Bala",
        'designation': "Supply Chain Solutions at UPS Supply Chain Solutions",
        'comment': "I’m so grateful to HasTech Info for helping me land my role with UPS Supply Chain Solutions. Their personalized mentorship and focus on real-world skills gave me the confidence to succeed.",
        'image_url': "/static/base_Asserts_images/"
    }

]

Domains_Url = [
    {
        "ID": 1,
        "Service_name": "Resume Optimization",
        "URL": "https://hashtechinfo.com/contact-us/",
        "logoImage": "/static/domain_images/",
        "smallDescription": "We refine your resume to highlight your strengths, skills, and experience, ensuring it stands out to recruiters and ATS systems."
    },
    {
        "ID": 2,
        "Service_name": "Profile Enhancement",
        "URL": "https://hashtechinfo.com/contact-us/",
        "logoImage": "/static/domain_images/",
        "smallDescription": "We optimize your LinkedIn and other professional profiles to boost visibility and attract the right opportunities."
    },
    {
        "ID": 3,
        "Service_name": "Job Matching",
        "URL": "https://hashtechinfo.com/contact-us/",
        "logoImage": "/static/domain_images/",
        "smallDescription": "We connect you with roles that align with your skills, experience, and career goals for the best job fit."
    },
    {
        "ID": 4,
        "Service_name": "Mock Interview Support",
        "URL": "https://hashtechinfo.com/contact-us/",
        "logoImage": "/static/domain_images/",
        "smallDescription": "We provide realistic interview simulations with expert feedback to improve your confidence and performance."
    },

    {
        "ID": 5,
        "Service_name": "Communication Skills Enhancement",
        "URL": "https://hashtechinfo.com/contact-us/",
        "logoImage": "/static/domain_images/",
        "smallDescription": "We help you refine your verbal and written communication to excel in professional interactions."
    },
    {
        "ID": 6,
        "Service_name": "Offer Negotiation",
        "URL": "https://hashtechinfo.com/contact-us/",
        "logoImage": "/static/domain_images/",
        "smallDescription": "We guide you in negotiating job offers effectively to secure the best salary and benefits package."
    }


]
json_schema = {
    "Most_Match_ROLE": {"type": "string"},
    "type": "object",
    "properties": {
        "Personal Information": {
            "type": "object",
            "properties": {
                "Name": {"type": "string"},
                "Phone number": {"type": "string"},
                "Email": {"type": "string"},
                "LinkedIn": {"type": "string"},
                "GitHub/portfolio": {"type": "string"}
            },
            "required": ["Name", "Phone number", "Email", "LinkedIn", "GitHub/portfolio"]
        },
        "Professional Summary": {"type": "string"},
        "Skills": {"type": "array", "items": {"type": "string"}},
        "Work Experience": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "Company": {"type": "string"},
                    "Title": {"type": "string"},
                    "Dates": {"type": "string"},
                    "Descriptions": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["Company", "Title", "Dates", "Descriptions"]
            }
        },
        "Education": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "Institution": {"type": "string"},
                    "Degree": {"type": "string"},
                    "Dates": {"type": "string"}
                },
                "required": ["Institution", "Degree", "Dates"]
            }
        },
        "Certifications": {
            "type": "array",
            "items": {"type": "string"}
        },
        "Projects": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "Title": {"type": "string"},
                    "Description": {"type": "string"},
                    "Technologies": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["Title", "Description", "Technologies"]
            }
        },
        "Other": {
            "type": "object",
            "properties": {
                "Strengths": {"type": "array", "items": {"type": "string"}},
                "Languages": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["Strengths", "Languages"]
        }
    },
    "required": ["Personal Information", "Professional Summary", "Skills", "Work Experience", "Education", "Certifications", "Projects", "Other"]
}

def Prompt_modifier(Document_data):
    return f"""
You are a resume and cover letter developer specializing in crafting professional, impactful resumes and cover letters tailored to various industries, job roles and give 'Most_Match_ROLE' like(software Engineer, data Analysist and data engineer..etc) based on skills and work experience . Follow **ATS (Applicant Tracking System) Keywords-Friendly Guidelines** and incorporate **SEO (Search Engine Optimized) keywords** to enhance visibility.

Extract structured information from the provided document and return it strictly in the following JSON format:
 

{{  "Most_Match_ROLE":"",
    "Personal Information": {{
        "Name": "",
        "Phone number": "",
        "Email": "",
        "LinkedIn": "",
        "GitHub/portfolio": ""
    }},
    "Professional Summary": "",
    "Skills": [],
    "Work Experience": [
        {{
            "Company": "",
            "Title": "",
            "Dates": "",
            "Descriptions": []
        }}
    ],
    "Education": [
        {{
            "Institution": "",
            "Degree": "",
            "Dates": ""
        }}
    ],
    "Certifications": [],
    "Projects": [
        {{
            "Title": "",
            "Description": "",
            "Technologies": []
        }}
    ],
    "Other": {{
        "Strengths": [],
        "Languages": []
    }}
}}

Ensure that:
- **All sections appear in the response** even if they have empty values.
- **Descriptions are in a list format** where applicable.
- **The JSON follows the exact structure above** without modifications.
- **make only 5 points for each work experience Descriptions it should be strict if given less content make is 5 lines if large content drop down and make it only 5.

Extract data from the following document:  
{Document_data}
"""
