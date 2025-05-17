from django.test import TestCase

from core.services.qdrant_service import QdrantRAGAgent


# Create your tests here.
def insert_knowledge_base_into_vector_db():
    """
    This function is a placeholder for the actual implementation that inserts a knowledge base into a vector database.
    It currently does nothing and is meant to be replaced with the actual logic.
    """
    collection_name = "newStudents"
    knowledge_base = [
          {
            "Questions": ["Why Anurag?", "Tell me about Anurag", "How to get admission?", "Is Anurag a private university?", "Where is Anurag University located?"],
            "Context": "Anurag University is a Private State University located in Hyderabad, Telangana. Our primary focus is to provide a high-quality education. Good education makes you competent. At Anurag, we believe that good education is just the beginning. We believe every student is capable of a lot more. We believe in helping you realize that potential. So, you are not just ready for the future, you are ready to make an impact on it."
          },
          {
            "Questions": ["What is the Telangana reservation rule?", "How are seats reserved in Anurag University?", "Are Telangana students given preference?"],
            "Context": "As per the Section 33 of the Telangana State Private Universities Act No. 11 of 2018, and Rule 10 of the G.O.Ms. No. 26 [HIGHER EDUCATION (UE.1) DEPARTMENT], Dt. 20-08-2019: 25% of seats for admissions in all the programs undertaken by the University shall be exclusively reserved for the students who studied for at least two years in the State of Telangana; Children whose parent/parents were born or worked for at least two years in the State of Telangana shall also be treated as students of Telangana for this purpose. Vacant seats will be open to the General Category."
          },
          {
            "Questions": ["Tell me about the AI program at Anurag", "What is taught in AI at Anurag?", "Is AI available as a course at Anurag?"],
            "Context": "Artificial Intelligence at Anurag University emphasizes learning, reasoning, and self-correction. It simulates human intelligence using computer systems. The course is designed to give students a strong foundation in AI principles like logic, knowledge representation, probabilistic models, and machine learning. Students learn to write and train machine learning algorithms. AI engineers are highly sought after across industries."
          },
          {
            "Questions": ["What does the IT course at Anurag include?", "Is there a cyber security program?", "What will I learn in IT at Anurag?"],
            "Context": "Information Technology at Anurag University involves planning, designing, and implementing applications using an architectural approach. Students learn computing, data storage, security, distributed systems, and communications. The course emphasizes the software development life cycle and databases along with strong technical skills. A specialization in Cyber Security is available, covering ethical hacking, network security, and digital forensics."
          },
          {
            "Questions": ["What is ECE at Anurag like?", "Is ECE offered at Anurag?", "Does Anurag have an R&D lab for ECE?"],
            "Context": "Electronics and Communication Engineering (ECE) at Anurag University focuses on communication technologies like satellites and smart devices. With advanced infrastructure including a full-fledged R&D lab and a modern curriculum, students are trained to excel in any career path. Anurag University is one of the top ECE colleges in Hyderabad."
          },
          {
            "Questions": ["Are scholarships available at Anurag?", "How to get a merit scholarship?", "What is the deadline for scholarships?"],
            "Context": "Anurag University offers merit scholarships based on performance in Anurag CET. Scholarships are automatically granted on admission or continued based on academic performance. To retain the scholarship, a student must maintain a CGPA of 8.0 or higher without backlogs. The deadline to apply for the Merit Scholarship for 2024–25 is October 17, 2024."
          },
          {
            "Questions": ["What is the fee structure at Anurag?", "How much does B.Tech cost?", "Is there an additional cost for minors or honors degrees?"],
            "Context": "Fee details at Anurag University:\n1. B.Tech (General): ₹1,35,000/year, 4 years, no extra charge for minors/honors.\n2. B.Tech in Artificial Intelligence: ₹2,85,000/year, 4 years, ₹10,000 extra for minors/honors.\n3. B.Tech in Information Technology with Cyber Security: ₹2,85,000/year, 4 years, ₹10,000 extra for minors/honors.\n4. B.Tech in Electronics & Computer Engineering: ₹2,85,000/year, 4 years, ₹10,000 extra for minors/honors. Fees follow TAFRC guidelines."
          },
          {
            "Questions": ["How are placements at Anurag?", "What is the placement process?", "Does Anurag help with job preparation?"],
            "Context": "Anurag University prepares students to be industry-ready with a strong foundation in coding, programming, and technical skills. The Training and Placement Division (TPD) supports students with skill training and career programs. The placement process includes: \n1. Pre-Process: Data capture, CV collection.\n2. Pre-Recruitment: Training, registration.\n3. Recruitment: Screening, interviews.\n4. Post-Recruitment: Announcements, feedback, analysis. AU students are given preference by recruiters due to their skill readiness."
          },
          {
            "Questions": [
              "What undergraduate engineering programs are offered at Anurag University?",
              "Which B.Tech courses can I pursue at Anurag University?",
              "Does Anurag University offer specialized engineering programs?"
            ],
            "Context": "Anurag University's School of Engineering offers a diverse range of undergraduate programs including B.Tech in Computer Science and Engineering, Artificial Intelligence, Artificial Intelligence & Machine Learning, Civil Engineering, Computer Science Engineering (Cyber Security), Computer Science Engineering (Data Science), Electronics and Communication Engineering, Electronics and Computer Engineering, Electrical and Electronics Engineering, Information Technology, and Mechanical Engineering. These programs are designed to equip students with both theoretical knowledge and practical skills in their chosen fields."
          },
          {
            "Questions": [
              "What postgraduate engineering programs are available at Anurag University?",
              "Can I pursue an M.Tech at Anurag University?",
              "What are the specializations offered in postgraduate engineering courses?"
            ],
            "Context": "Anurag University's School of Engineering offers postgraduate programs including M.Tech in Computer Science and Engineering, Power Electronics and Electrical Drives, Structural Engineering, and VLSI Design. These programs focus on advanced topics and research opportunities, preparing students for specialized roles in the engineering industry."
          },
          {
            "Questions": [
              "What research opportunities does Anurag University provide in engineering?",
              "Can I pursue a Ph.D. in engineering at Anurag University?",
              "What are the research areas in the School of Engineering?"
            ],
            "Context": "Anurag University's School of Engineering emphasizes research and development, offering Ph.D. programs in various disciplines such as Computer Science, Mechanical Engineering, Civil Engineering, Electrical & Electronics Engineering, and more. The university has several research centers focusing on areas like Artificial Intelligence and Machine Learning, Cyber Security, VLSI Design, Renewable Energy, and Structural Engineering. Faculty and students collaborate on funded research projects, and the university encourages publication in reputed journals."
          },
          {
            "Questions": [
              "What facilities are available at Anurag University's School of Engineering?",
              "Does Anurag University have modern infrastructure for engineering students?",
              "What kind of laboratories and resources are provided?"
            ],
            "Context": "Anurag University's School of Engineering boasts state-of-the-art infrastructure including advanced laboratories for each discipline, dedicated labs for AI, IoT, Robotics, VLSI, and more. The campus features a central library with a vast collection of resources, Wi-Fi enabled classrooms, seminar halls, and conference rooms. Additionally, there are separate hostels for boys and girls, sports complexes, gymnasium, cafeteria, and medical facilities to ensure a comprehensive learning environment."
          },
          {
            "Questions": [
              "What extracurricular activities are available for engineering students?",
              "Does Anurag University organize technical and cultural events?",
              "Are there student clubs and societies in the School of Engineering?"
            ],
            "Context": "Anurag University's School of Engineering encourages holistic development through various extracurricular activities. Students can participate in annual technical festivals like 'Technospectrum', cultural events such as 'ANURAAG', and sports tournaments. The university hosts numerous clubs and societies including the Coding Club, Robotics Club, Literary Society, and Entrepreneurship Cell, providing platforms for students to explore and enhance their skills beyond academics."
          },
          {
            "Questions": [
              "What are the placement opportunities for engineering students at Anurag University?",
              "Which companies recruit from Anurag University's School of Engineering?",
              "What is the average salary package offered?"
            ],
            "Context": "Anurag University's School of Engineering has a strong placement record, attracting top recruiters like Microsoft, Amazon, TCS, Wipro, Cognizant, Accenture, Infosys, Tech Mahindra, and Deloitte. The university's dedicated placement cell offers career counseling, soft skill training, and technical workshops to prepare students for the industry. The average salary package ranges from INR 5 to 10 LPA, with higher packages for top performers, especially in fields like computer science and data science."
          },
          {
            "Questions": [
              "What accreditations and rankings does Anurag University's School of Engineering hold?",
              "Is Anurag University recognized by national bodies?",
              "What are the university's achievements in engineering education?"
            ],
            "Context": "Anurag University's School of Engineering is accredited with an 'A' grade by the National Assessment and Accreditation Council (NAAC) and several B.Tech programs are accredited by the National Board of Accreditation (NBA). The university is recognized by AICTE and is included in 2(f) & 12(B) of the UGC Act. It has been ranked among the top engineering institutions in Telangana and has a growing national presence."
          },
          {
            "Questions": [
              "What is the admission process for engineering programs at Anurag University?",
              "Which entrance exams are accepted for B.Tech admissions?",
              "How can I apply for engineering courses at Anurag University?"
            ],
            "Context": "Admissions to Anurag University's engineering programs are based on performance in entrance examinations such as TS EAMCET, JEE Main, or through the university's own entrance exam (AUEET). Candidates are selected based on their scores and academic merit. The university provides detailed information and guidance on the application process through its official website."
          }
    ]
    QdrantRAGAgent(collection_name=collection_name).create_collection(
        knowledge_base=knowledge_base)