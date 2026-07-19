import asyncio
import json
from api.v1.routes.jobs import generate_or_edit_jd

async def main():
    user_id = "user@email.com"
    raw_input = "We are looking for a Senior Software Engineer with expertise in Python and cloud technologies. The ideal candidate will have experience in building scalable applications, working with microservices architecture, and deploying solutions on AWS or Azure. Responsibilities include designing, developing, and maintaining software solutions, collaborating with cross-functional teams, and ensuring code quality through testing and code reviews. The candidate should also be familiar with CI/CD pipelines and agile methodologies."
    
    res = await generate_or_edit_jd(user_id, raw_input)
    print("\n====== FINAL OUTPUT ======\n")
    print(res.raw if hasattr(res, 'raw') else res)

if __name__ == "__main__":
    asyncio.run(main())