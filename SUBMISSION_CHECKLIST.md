# Submission checklist

## Final verification

- [ ] Run `pip install -r requirements.txt` in a clean virtual environment.
- [ ] Run `pytest -q`.
- [ ] Run `python evals/run_evals.py`; confirm all 10 cases pass.
- [ ] Test both Streamlit tabs and FastAPI `/docs`.
- [ ] Confirm `.env` is absent and `.env.example` has no key.
- [ ] Scan the repository for secrets before pushing.

## GitHub commands

```bash
git init
git add .
git commit -m "Complete Zycus AI support internship assignment"
git branch -M main
git remote add origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main
```

Verify repository access in an incognito window.

## Loom

- [ ] Record approximately 10 minutes using `LOOM_SCRIPT.md`.
- [ ] Explain approach, methodology/tools, implementation, decisions, and outcomes.
- [ ] Show both live tasks and evaluation results.
- [ ] Enable link access and test the URL.

## Submission email

**Subject:** AI Engineer - Product Support Intern Assignment Submission - Pratik Naikwade

Dear Amit,

Thank you for the opportunity. I have completed the AI Engineer - Product Support Intern assessment.

GitHub repository: [paste GitHub link]  
Loom walkthrough: [paste Loom link]

The repository includes setup instructions, live demos for both tasks, the evaluation harness and report, and the design note.

Please let me know if you need any additional information.

Best regards,  
Pratik Naikwade

