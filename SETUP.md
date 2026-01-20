# Quick Setup Guide

## Install Required Packages

Run this command to install all dependencies:

```bash
pip install pandas openpyxl python-dotenv langchain-google-genai langchain-core
```

Or use the requirements file:

```bash
pip install -r requirements.txt
```

## Verify Installation

```bash
python -c "from integrated_hr_agent import IntegratedHRAgent; print('✅ Setup successful!')"
```

## Run the Demo

```bash
python demo.py
```

Choose:
- **Option 1**: Guided workflow demo (recommended for first run)
- **Option 2**: Interactive mode for manual testing

## Quick Test

For a quick test with default values:
1. Run `python demo.py`
2. Select option `1`
3. Press Enter for all prompts (uses defaults)
4. Watch the AI analyze and make decisions!

## Troubleshooting

**Error: "No module named 'pandas'"**
→ Run: `pip install pandas openpyxl`

**Error: "No module named 'langchain_google_genai'"**
→ Run: `pip install langchain-google-genai langchain-core`

**Error: "Teacher not found"**
→ Check that the teacher name exists in `employees.xlsx`

**Error: "API key not found"**
→ Make sure `.env` file has `GOOGLE_API_KEY=your_key_here`
