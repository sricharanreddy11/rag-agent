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

def insert_syllabus_data():
    knowledge_base = [
          {
            "course": "Memories for embedded systems",
            "branch": "ECE",
            "level": "Intermediate",
            "description": "Designed for intermediate learners, this PDF provides a structured understanding of embedded system components like ROM/RAM memory types, sensor-actuator functions, and both onboard and external communication interfaces. It introduces concepts like memory shadowing and explains protocols like I2C and SPI with moderate technical depth. Each topic balances clarity and detail, preparing students to analyze embedded system requirements and choose appropriate components. It's well-suited for 3rd-year B.Tech ECE students ready to transition from basic understanding to hands-on application in labs or mini-projects.",
            "link": "https://drive.google.com/file/d/1wad3iaRuI0vLEpm73vwLV9vV2tB1AtDp/view?usp=sharing"
          },
          {
            "course": "Memories for embedded systems",
            "branch": "ECE",
            "level": "Beginner",
            "description": "This beginner-friendly guide introduces the fundamentals of embedded systems, focusing on memory, sensors, actuators, and communication interfaces. It simplifies concepts using analogies and examples, like using ROM as a recipe book or explaining Bluetooth as a song-sharing method. The content is ideal for students new to embedded systems, helping them understand how devices sense the environment, store data, perform actions, and communicate. With visuals and relatable language, it builds a strong conceptual foundation while keeping technical terms minimal, making it perfect for those starting their embedded systems journey.",
            "link": "https://drive.google.com/file/d/1ZHd0ss3ufTSU6G5LIEg7CR0csduJ6a6T/view?usp=sharing"
          },
          {
            "course": "Memories for embedded systems",
            "branch": "ECE",
            "level": "Advanced",
            "description": "This document delivers an advanced exploration of embedded system architecture, offering in-depth analysis of memory hierarchies, ROM/RAM variants, and data communication protocols. It includes precise timings, operational principles, and trade-offs, such as SRAM vs. DRAM, I2C vs. SPI, and communication latency. With complex technical language and real-world examples (e.g., BIOS shadowing, industrial memory), it is tailored for students preparing for research, design projects, or interviews. Ideal for final-year B.Tech ECE students aiming for mastery in embedded system design and optimization.",
            "link": "https://drive.google.com/file/d/1wad3iaRuI0vLEpm73vwLV9vV2tB1AtDp/view?usp=sharing"
          },
          {
            "course": "Antennas",
            "branch": "ECE",
            "level": "Beginner",
            "description": "This PDF is designed as a beginner-friendly guide to the basics of antennas, ideal for 2nd-year ECE students new to the subject. It explains fundamental concepts like what antennas are, how they work, and their everyday applications using simple analogies and relatable examples. Key topics include types of antennas (isotropic, directional, and omni-directional), how antennas transmit and receive electromagnetic waves, and how they are used in devices such as smartphones, radios, and airplanes like the Boeing 787. Concepts like radiation patterns, main lobes, side lobes, and antenna size are introduced without mathematical complexity. The document keeps the tone light and engaging with \"fun facts\" and practical illustrations. It builds a strong conceptual foundation while sparking curiosity about real-world communication systems. This is an excellent first step for students preparing to dive deeper into electromagnetic theory and antenna design.",
            "link": "https://drive.google.com/file/d/1uc4J4nDwJByrawE3OdKhYgUUqx4SJemA/view?usp=sharing"
          },
          {
            "course": "Antennas",
            "branch": "ECE",
            "level": "Intermediate",
            "description": "This intermediate-level guide provides a structured yet accessible exploration of antenna concepts tailored for students with basic knowledge of electromagnetic theory. It covers how antennas operate as transducers, converting electrical signals to electromagnetic waves and vice versa. Topics include radiation mechanisms (time-varying current and charge acceleration), transmission line modeling of antennas using Thevenin equivalents, and practical uses in systems like smartphones, radar, and aviation (e.g., Boeing 787 communication). The document explains technical parameters such as beamwidth, radiation intensity, field regions (near-field and far-field), and directivity with simplified equations and contextual examples. Students also learn about antenna efficiency and the reciprocity theorem, helping them understand both theoretical and applied aspects. This guide is ideal for ECE students seeking a balance between conceptual clarity and moderate technical depth—perfect for exam prep, lab understanding, or early-stage design projects.",
            "link": "https://drive.google.com/file/d/1Cddh4_R70bZCh7H0t-5wAWCgh6YkdkIn/view?usp=sharing"
          },
          {
            "course": "Antennas",
            "branch": "ECE",
            "level": "Advanced",
            "description": "This advanced-level document is a comprehensive, high-depth resource on antenna theory, ideal for academically strong 2nd-year ECE students or those preparing for competitive exams and advanced projects. It begins with antenna fundamentals and radiation mechanisms and dives deep into technical models, including current density and radiation conditions. Students are introduced to rigorous analytical tools such as normalized field/power patterns, beam solid angles, Thevenin equivalent circuits, and the Poynting vector. The guide extensively discusses beamwidth analysis (HPBW, FNBW), field regions (reactive, radiating, and far-field), radiation intensity, and antenna efficiency. Complex formulas for directivity, aperture efficiency, and the front-to-back ratio are derived with examples. The inclusion of solid angle calculus, radiation power calculations, and advanced metrics like stray factor and reciprocity make this resource suitable for students aiming to master electromagnetic theory. It demands good mathematical skills and understanding of EMTL concepts, offering a solid foundation for research or higher-level engineering design.",
            "link": "https://drive.google.com/file/d/1tvs5YTuYKaFNvXqEUvXOFjSn9xf2TI3z/view?usp=sharing"
          },
          {
            "course": "Introduction to Computer Vision and Basic Concepts of Image Formation",
            "branch": "AI",
            "level": "Intermediate",
            "description": "This intermediate-level guide bridges conceptual basics and practical application in CVIP. It expands on image types, storage calculations, sampling, and quantization with mathematical models like f(x, y) = i(x, y) × r(x, y). It introduces geometric projection models and CCD/CMOS sensor differences while emphasizing resolution, color depth, and file size. Applications include robotics, AR, and medical diagnostics. Designed for students with foundational knowledge in image processing, this version explains both the physical and computational aspects of image formation and prepares learners for hands-on coding, project implementation, or further academic study in AI and vision systems.",
            "link": "https://drive.google.com/file/d/11fhTjt2Mn-ZKURSBTFWKM76OEFZww-qc/view?usp=sharing"
          },
          {
            "course": "Introduction to Computer Vision and Basic Concepts of Image Formation",
            "branch": "AI",
            "level": "Beginner",
            "description": "This beginner guide introduces Computer Vision & Image Processing in a simple, engaging way. It covers what CV is, where it's used (like face unlock, self-driving cars, and healthcare), and how images are captured, stored, and represented using pixels. Core topics like image types (binary, grayscale, RGB), resolution, sampling, and quantization are explained with real-life examples. Students learn how cameras work using light, lenses, and sensors, building a solid foundation for further learning. Ideal for students with no prior exposure to CVIP, this document makes the subject approachable and relevant using illustrations and simplified definitions.",
            "link": "https://drive.google.com/file/d/16bqDj4RqJGnzNSyaZAkqvdu2OoT4A4Hr/view?usp=sharing"
          },
          {
            "course": "Introduction to Computer Vision and Basic Concepts of Image Formation",
            "branch": "AI",
            "level": "Advanced",
            "description": "The advanced guide offers an in-depth exploration of CVIP, covering mathematical models, pinhole camera projections, photometric stereo, radiometric functions, and multidimensional image representations. It emphasizes real-world engineering applications like HDR imaging, structure-from-motion, and image warping. Tools like OpenCV, MATLAB, and TensorFlow are discussed alongside research references. Designed for high-level learners or project-driven students, this version includes derivations, advanced storage calculations, and analytical comparisons (e.g., CCD vs. CMOS). It is perfect for students pursuing research, internships, or advanced CV-based projects, blending theory, math, and professional tools for a comprehensive CVIP understanding.",
            "link": "https://docs.google.com/document/d/11yfdup3AnsetZRJ5hgwRR5Buegei6HCU/edit?usp=sharing&ouid=104608362266216366007&rtpof=true&sd=true"
          },
          {
            "course": "Introduction to Database System Concepts",
            "branch": "AI",
            "level": "Intermediate",
            "description": "Tailored for 2nd-year B.Tech AI students (R22 regulation), this intermediate-level guide for Unit 1 of Data Structures explores arrays, linked lists, stacks, expression conversion, and Tower of Hanoi. It emphasizes time/space complexity, with code snippets for operations like linked list insertion and infix-to-postfix conversion. Real-world examples, such as stacks for undo operations, enhance understanding. Practice questions, YouTube links (e.g., Gate Smashers), and an 8.5-hour study plan support learning. This guide bridges foundational knowledge and advanced concepts, preparing students for efficient algorithm implementation and problem-solving.",
            "link": "https://docs.google.com/document/d/1HPWhUABOOHT_dx7gvHAJz67Il43kn4fa/edit?usp=sharing&ouid=104608362266216366007&rtpof=true&sd=true"
          },
          {
            "course": "Introduction to Database System Concepts",
            "branch": "AI",
            "level": "Beginner",
            "description": "This beginner-level study guide for 2nd-year B.Tech AI students (R22 regulation) introduces Unit 1 of Data Structures, covering arrays, linked lists, stacks, expression conversion, and Tower of Hanoi. It provides simple definitions, real-world examples like arrays for temperature readings, and basic code snippets. Key concepts include linear vs. non-linear structures and ADTs. Practice questions, YouTube resources (e.g., Jenny's Lectures), and time management tips (e.g., 1-hour reading) aid learning. Designed for foundational understanding, it ensures students grasp data organization and basic operations for efficient algorithm design.",
            "link": "https://docs.google.com/document/d/14_282auyhL-z4Rqwf_bQP_w9ytDk31Kq/edit?usp=sharing&ouid=104608362266216366007&rtpof=true&sd=true"
          },
          {
            "course": "Introduction to Database System Concepts",
            "branch": "AI",
            "level": "Advanced",
            "description": "This advanced-level study guide for 2nd-year B.Tech AI students (R22 regulation) dives deep into Unit 1 of Data Structures, covering arrays, linked lists, stacks, expression conversion, and Tower of Hanoi. It focuses on memory models, recursion analysis (e.g., O(2ⁿ) for Hanoi), and optimization techniques like dynamic arrays. Complex operations, such as reversing linked lists and postfix evaluation, are detailed with code. Real-time applications (e.g., compilers) and practice questions are included. With YouTube resources, an 11.5-hour study plan, and textbook references (e.g., CLRS), it equips students for scalable, efficient algorithm design.",
            "link": "https://docs.google.com/document/d/1f-iD8pwGFfCeWzz4fXt16fRXBjw5VMML/edit?usp=sharing&ouid=104608362266216366007&rtpof=true&sd=true"
          },
          {
            "course": "Overview of Artificial Intelligence: Introduction.",
            "branch": "IT",
            "level": "Intermediate",
            "description": "This is engages 3rd-year B.Tech IT students under R22 regula tion with a conversational AI overview. It explores the Turing Test, Weak vs. Strong AI, heuristics, and AI-suitable problems (e.g., MYCIN, barcode scanners). Practical exam ples like Netflix recommendations and the Water Jug problem make concepts accessible. Covering AI methods (search algorithms, neural networks) and history (Aristotle to Deep Blue), it balances theory and application. Suited for students with some AI exposure, it supports R22's curriculum by illustrating AI's impact in healthcare and technology, fostering understanding through a student-friendly narrative and real-world relevance",
            "link": "https://drive.google.com/file/d/1c7u_yrOPWi4AvrxHAO-jagNW7YSvBQSM/view?usp=sharing"
          },
          {
            "course": "Overview of Artificial Intelligence: Introduction.",
            "branch": "IT",
            "level": "Advanced",
            "description": "This challenges 3rd-year B.Tech IT students under R22 reg ulation with a technical AI exploration. It delves into AI's interdisciplinary foundations, the Turing Test's limitations, Strong vs. Weak AI debates, and heuristic algorithms (e.g., A* search). Complex applications like AlphaFold and Google Maps showcase AI's capa bilities. It details knowledge representation, history (Aristotle to Watson), and modern advancements (Tesla's Autopilot). With theoretical insights and ethical discussions, it aligns with R22's advanced AI curriculum, equipping students to analyze AI's technical and philosophical dimensions in robotics, finance, and beyond, ideal for those with strong 1 AI foundations.",
            "link": "https://drive.google.com/file/d/1lYVA4r-qX_jM8QE7IqQp-oofVhTOBZcB/view?usp=sharing"
          },
          {
            "course": "Overview of Artificial Intelligence: Introduction.",
            "branch": "IT",
            "level": "Beginner",
            "description": "This is ideal for 3rd-year B.Tech IT students starting AI under R22 regulation. It simplifies Artificial Intelligence concepts, covering definitions, the Turing Test, Strong vs. Weak AI, heuristics, and applications like Siri and chess. With clear examples (e.g., Google Translate, Missionaries and Cannibals), it explains AI's role in games and medicine. The PDF traces AI's history from Aristotle to Deep Blue and modern self-driving cars, using straightforward language. Aligned with R22's founda tional curriculum, it helps beginners grasp AI's basics, making smart systems relatable through everyday technology, preparing students for further AI studies",
            "link": "https://drive.google.com/file/d/1Fgo0rDSHj4OOREPp5mIgSSKdPc8MqwvG/view?usp=sharing"
          },
          {
            "course": "Introduction to Database System Concepts",
            "branch": "IT",
            "level": "Intermediate",
            "description": "Designed for 3rd-year B.Tech IT students (R22 regulation), this intermediate-level guide for DBMS Unit 1 explores DBMS, database vs. file systems, characteristics, users, advantages, disadvantages, data models, schema, three-tier architecture, and client-server architecture. It introduces time complexity (e.g., O(log n) for indexed queries) and concepts like referential integrity. Examples include retail inventory systems. Practice questions, a structured 8-hour study plan, and resources like Neso Academy videos support learning. This guide bridges basics to advanced topics, equipping students for efficient database design and query optimization",
            "link": "https://drive.google.com/file/d/1EniPE4BR32rDx3k68fwCUXy44VW0t6cY/view?usp=sharing"
          },
          {
            "course": "Introduction to Database System Concepts",
            "branch": "IT",
            "level": "Advanced",
            "description": "This advanced-level guide for 3rd-year B.Tech IT students (R22 regulation) delves into DBMS Unit 1, covering DBMS, file systems, characteristics, users, advantages, disadvantages, data models, schema, three-tier, and client-server architectures. It emphasizes distributed systems, ACID transactions, and query optimization (e.g., O(log n) with B+ trees). Real-world cases like Google Spanner and DynamoDB highlight scalability. Practice questions focus on system design (e.g., sharding), with an 11.5-hour study plan and resources like Jenny's Lectures. It prepares students for complex database challenges in distributed and high-performance environments.",
            "link": "https://drive.google.com/file/d/1CPT0zfrOrSf4Q8wJCbgdIttKDOBrz95q/view?usp=sharing"
          },
          {
            "course": "Introduction to Database System Concepts",
            "branch": "IT",
            "level": "Beginner",
            "description": "This beginner-level guide for 3rd-year B.Tech IT students (R22 regulation) introduces DBMS Unit 1, covering DBMS basics, database vs. file systems, characteristics, users, advantages, disadvantages, data models, and schema concepts. It uses simple explanations, like comparing a DBMS to a digital librarian, with examples such as school record systems. Key points include organized storage, security, and relational models. Practice questions and study tips (e.g., 1-hour reading) enhance understanding. Ideal for foundational learning, it prepares students to grasp database management and its benefits over manual systems",
            "link": "https://drive.google.com/file/d/1CPT0zfrOrSf4Q8wJCbgdIttKDOBrz95q/view?usp=sharing"
          }
        ]
    QdrantRAGAgent(collection_name="tutorKB").create_collection(knowledge_base=knowledge_base)