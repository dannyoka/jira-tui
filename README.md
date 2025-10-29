# Jira TUI

A terminal-based Textual UI for browsing, searching, and commenting on Jira issues assigned to you.

## Features

- View issues assigned to you in a split-pane interface (like Lazygit)
- See issue details and comments
- Add comments to issues
- Keyboard navigation (vim-like: `j`, `k`, `h`, `l`, etc.)

## Installation

1. **Clone the repository:**

   ```sh
   git clone https://github.com/yourusername/jira-tui.git
   cd jira-tui
   ```

2. **Install dependencies:**

   ```sh
   pip install -r requirements.txt
   ```

   _(Requires Python 3.8+)_

## JIRA Authentication Setup

This tool uses environment variables for Jira authentication.  
Add the following to your `.zshrc` (or `.bashrc` if you use bash):

```sh
export JIRA_EMAIL="your.email@company.com"
export JIRA_API_TOKEN="your_jira_api_token"
export JIRA_URL="https://yourcompany.atlassian.net"
```

After editing, reload your shell:

```sh
source ~/.zshrc
```

## Usage

Run the app from your project directory:

```sh
python -m jira_tui
```

or

```sh
python jira_tui/main.py
``
```
