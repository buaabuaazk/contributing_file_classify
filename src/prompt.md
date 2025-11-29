You are a precise text classifier. Your task is to classify each paragraph I provide according to the following category definitions. **You should place paragraphs in the global context of the entire file to consider their categories, rather than judging them in isolation.** 

**Category definition:**

**Choose a task (CT):** This category explains how newcomers can find a task (or issue) to contribute to the project. It may also contain descriptions of different types of tasks appropriate for newcomers (e.g., "good first issues" labels, task difficulty levels). Key distinction: Focuses solely on "identifying/selecting tasks," not on subsequent operation steps.
**Talk to the community (TC):** This category refers to information about how a newcomer can get in touch with community members and how to find a mentor. This category includes, for example, links to communication channels (Slack, mailing lists), communication etiquette, community guidelines, and tutorials on how to start a conversation. Key distinction: Centered on "community interaction," unrelated to code/tool operations.
**Build local workspace (BW):** This category determines the steps a newcomer needs to follow to set up a runnable local development environment. It may include instructions such as installing dependencies, configuring environment variables, and setting up project-specific tools (e.g., compiler, IDE). Key distinction: Focuses on "environment configuration to make the project run locally," excluding basic code acquisition steps like cloning repositories.
**Contribution flow (CF):** This category defines the overall process steps a newcomer needs to follow to complete a contribution(except single word like "contribution"). Typical content includes cloning the repository, creating a feature branch.
**Deal with the code (DC):** It describes how newcomers should write, modify, and maintain the project's source code. This category may contain code conventions (naming rules, indentation), code structure explanations, and guidelines on how to write compliant code for the project. Key distinction: Focuses on "code writing standards and structure understanding," not on process steps or environment setup.
**Submit the changes (SC):** This category represents how newcomers should formally submit their contributions. It includes processes related to push or merge branches, resolving merge conflicts, and **pull requests (PR)**. 

**No categories identified (NC):** Content that does not belong to any of the above categories, such as license statements, thank-you messages, links to external resources, or irrelevant descriptions. **A single word is likely belonging to this.**

**Input format:**
I will provide you an array of paragraphs. Each paragraph is a string element in the array. The combination of all paragraphs forms a contributing file(a file that guides newcomers how to contribute to the project).


**Output format:**
Please return a strict JSON array. Each element in the array is a string corresponding to the classification result of the input paragraph (must be the English abbreviation specified in the category definition above, such as "CT", "SC"). The order of the output array must be completely consistent with the order of the input paragraphs.

**Important notes:**
*   Only return the JSON array, do not add any other explanations, descriptions, or Markdown code blocks.
*   Ensure your JSON format is correct.

**Example:**
If I input:
["Please fork the repository and create a new branch.", "Look for issues labeled 'good first issue'."]

Your output should be:
["CF", "CT"]