# ComfyUI Artist Tester

A dedicated suite of Custom Nodes for **Batch Testing** artists, styles, and prompts in ComfyUI. 

Designed to solve the "caching" problem where batch runs produce identical images, and simplifies the workflow for saving images with dynamic filenames.

## ✨ Features

- **👉 1. Artist List Iterator**
  - **Auto Increment Mode**: Automatically iterates through your list (one per batch). No external primitive nodes needed.
  - **Reset Function**: A simple boolean switch to reset the counter to 0.
  - **Anti-Cache**: Built-in logic to force ComfyUI to re-generate every single time.
  
- **👉 2. Artist Prompt Station**
  - Combines `Base Prompt` + `Artist Tag` + `Negative Prompt` automatically.
  - Outputs **Positive & Negative Conditioning** (plug & play).
  - Outputs **Final Text String** (for filenames).

- **💾 3. Save Image (Auto Name)**
  - **Smart Sanitization**: Automatically fixes filenames that cause Windows errors!
    - Converts `artist:tag` to `artist-tag`.
    - Removes illegal characters (`\ / : * ? " < > |`).
    - Truncates overly long filenames.
  - Connect the "Final Text" or "Artist Tag" directly to the `filename_prefix` input.

## 📦 Installation

1. Open your terminal/command prompt.
2. Navigate to your ComfyUI custom nodes directory:
   ```bash
   cd ComfyUI/custom_nodes/
   Clone this repository:
   git clone https://github.com/g7b2/ComfyUI-Artist-Tester.git
