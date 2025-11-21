xcellent — here’s the **expanded version** of your Visual Studio Code guide, now including a concise “Rollback Guide” section.
This will be saved as:
📄 **`/src/docs/GIT_COMMIT_GUIDE.md`**

---

# **GIT COMMIT GUIDE — SEA-SEQ v1.2.0 (Security Annotated Edition)**

**Author:** @reggiemoorejr
**Version:** SEA-SEQ v1.2.0 — Security Annotated Edition
**Last Updated:** October 2025

---

## 🎯 **Purpose**

This guide explains how to **commit, tag, push, and (if needed) roll back** SEA-SEQ updates inside **Visual Studio Code (VS Code)** — all without using any Git terminal commands.

---

## 🧭 **Step-By-Step — Using VS Code Only**

### **1️⃣ Open the SEA-SEQ Folder**

1. Launch **Visual Studio Code**.
2. Select **File → Open Folder…**.
3. Choose your local SEA-SEQ project folder (the one containing `/src`).

---

### **2️⃣ Open Source Control**

1. On the **left sidebar**, click the **Source Control (Git)** icon.
   *(It looks like a Y-shaped branch symbol.)*
2. VS Code will list all modified files since your last commit.

---

### **3️⃣ Stage the Changes**

1. Hover over each modified file (for example: `pentest_runner.py`, `Dockerfile`, `destroydata.sh`).
2. Click the **➕ (plus icon)** next to each file to stage it.
3. Staged files appear under **“Staged Changes.”**

---

### **4️⃣ Add the Commit Message**

1. Open `src/docs/commit_message.txt`.
2. **Select All → Copy** the message text.
3. Go back to the **Source Control panel**.
4. Paste it into the **commit message box** at the top.
5. Review for accuracy (especially the version tag).

---

### **5️⃣ Commit the Changes**

1. Click the **✔ Commit** button.
2. VS Code confirms your commit at the top or bottom status bar.
3. Your files now appear in repository history.

---

### **6️⃣ Push Your Commit to GitHub**

1. Click the **⋯ (three dots)** menu in the Source Control panel.
2. Select **Push → Push to Origin**.
3. VS Code uploads your changes to GitHub.
4. Confirmation appears: *“Successfully pushed to origin/main.”*

---

### **7️⃣ Add a Version Tag (Optional in GUI)**

1. In **Source Control**, open the **View → SCM: Tags** section.
2. Click **Create Tag** → name it **v1.2.0**.
3. Add a short description:
   *“SEA-SEQ v1.2.0 — Security Annotated Edition.”*
4. Right-click the tag → **Push Tag to Origin**.

---

### **8️⃣ Verify on GitHub**

1. Go to your **GitHub repository** → **Releases** tab.
2. You’ll see:

   * The commit message
   * Tag `v1.2.0`
   * Linked changelog and release notes

---

## 🔄 **Rollback Guide (Undo a Commit in VS Code)**

Sometimes you commit too early or catch an error right after pushing. Here’s how to roll back safely — all from within VS Code.

---

### **Option 1: Undo a Commit (Before Pushing)**

1. Open the **Source Control** panel.
2. Click the **⋯ (three dots)** menu.
3. Select **Undo Last Commit**.
4. VS Code will:

   * Unstage your changes
   * Restore them in the working directory
   * Remove the last commit message

🧠 **Tip:** You can now fix files or edit your commit message, then recommit normally.

---

### **Option 2: Revert a Commit (After Pushing)**

1. Open the **Source Control → Timeline** view (right-click a file → “Open Timeline”).
2. Find the commit you want to revert.
3. Right-click → **Revert Commit**.
4. VS Code creates a new “undo” commit that reverses those changes safely.

🧠 **Best Practice:** Always **revert**, not delete, after pushing — this keeps team history clean.

---

### **Option 3: Discard Local File Changes**

1. If you haven’t committed yet:

   * Right-click the changed file.
   * Choose **Discard Changes**.
2. VS Code restores the file to its last committed version.

⚠️ **Warning:** This can’t be undone — only use if you’re sure you don’t need the current edits.

---

## ✅ **Done**

You’ve successfully learned how to commit, tag, push, and roll back changes in **Visual Studio Code** — all without typing a single Git command.

---

## 💡 **Tips**

* Use **Source Control → Timeline** to track each file’s change history.
* Review staged files carefully before each commit.
* Always verify tags and version numbers before pushing to origin.
* Keep `commit_message.txt` updated for each new release version.

--