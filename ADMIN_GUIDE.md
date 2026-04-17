# Admin Guide

## Getting Access

Contact the site administrator to create an account and assign you to the appropriate volunteer group. Your role determines what you can do on the dashboard.

| Role | Permissions |
|---|---|
| Curator | Download and curate submitted question datasets |
| Encoder | Encode curated datasets into the database |
| Answer Writer | Write answers to questions |
| Answer Reviewer | Review and publish answers |
| Translator | Translate questions, answers, and articles |
| Article Writer | Write and submit articles |

---

## The Question Workflow

Questions submitted by users go through the following stages before being published:

```
Submission → Curation → Encoding → Answered → Reviewed → Published
```

---

## Curating Datasets

When a new batch of questions is submitted, they appear in the **Curate Data** section.

1. Go to **Dashboard → Curate Data**
2. You will see a table of recent submissions with a **Link** to download each Excel file
3. Download the Excel file — it contains all the submitted questions
4. Fill in the **Field of Interest** column for each question (e.g. Biology, Physics, Chemistry, etc.)
   - Do not edit any other column or the file will be rejected
   - The `dataset_id` column must remain unchanged
5. Save the file and upload it back using the **Submit Curated Dataset** form on the same page
6. Django reads the file and saves all questions into the database
7. The questions are now available for answering and translation

---

## Writing Answers

1. Go to **Dashboard → Answer Questions**
2. Pick a question and write your answer
3. Submit the answer — it goes to a reviewer before being published

---

## Reviewing Answers

1. Go to **Dashboard → Review Answers**
2. Read the submitted answer
3. Approve to publish it, or send it back with feedback

---

## Translating Content

1. Go to **Dashboard → Translate**
2. Select a language and content type (question, answer, or article)
3. Submit the translation — it goes through the same draft → submitted → published workflow

---

## Writing Articles

1. Go to **Dashboard → Write Article**
2. Write and submit your article
3. A reviewer will approve it before it is published on the public site

---

## Dashboard Stats

The dashboard home page shows live stats updated every hour:

- **Total Users** — registered users on the platform
- **Pending Access Requests** — volunteer requests awaiting approval
- **New Datasets** — question batches not yet curated
- **Unanswered Questions** — questions with no published answer
- **Unreviewed Answers** — answers awaiting review
- **Items to Translate** — total content needing translation

---

## Managing Users

Admins can manage volunteer access requests under **Dashboard → Manage Users**:

- Approve or reject volunteer requests
- Assign users to groups (Curator, Encoder, etc.)

---

## Approving Volunteer Requests

When a user requests volunteer access:

1. Go to **Dashboard → Access Requests**
2. Review the request
3. Approve and assign them to the appropriate group, or reject with a reason

---

## Accessing Raw Submission Files

When questions are submitted, two copies of the Excel file are saved on the server:

- **Uncurated file** — available via the download link in the dashboard (has extra columns added for curation)
- **Raw file** — an exact copy of the original submission, kept as a backup archive

The raw files are not accessible through the website. To access them, an administrator needs to SSH into the server.

### SSH into the server

```bash
ssh user@sawaliram.org
```

### Find the raw files

```bash
docker exec django-sawaliram-app ls uploads/submissions/raw/
```

Files are named `dataset_<id>_raw.xlsx`.

### Copy a file to your local machine

Run this on your **local machine** (not the server):

```bash
scp user@sawaliram.org:/var/lib/docker/volumes/sawaliram_uploads/_data/submissions/raw/dataset_1_raw.xlsx .
```

Replace `dataset_1_raw.xlsx` with the filename you want.

### Find uncurated files

```bash
docker exec django-sawaliram-app ls uploads/submissions/uncurated/
```

These are the same files available via the dashboard download link. If the link is broken for any reason, you can copy them the same way:

```bash
scp user@sawaliram.org:/var/lib/docker/volumes/sawaliram_uploads/_data/submissions/uncurated/dataset_1_uncurated.xlsx .
```

---

## Common Issues

**I can't see a section in the dashboard**
You may not have the required group permissions. Contact the site administrator.

**The download link for a dataset returns a 404**
The Excel file may not have been generated correctly during submission. Check with the administrator.

**My answer was sent back for revision**
Check the reviewer's feedback and update your answer before resubmitting.
