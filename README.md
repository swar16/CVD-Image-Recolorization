# CVD Image Recolorization

This repository contains a project focused on **recoloring images for individuals with Color Vision Deficiency (CVD)**, commonly known as color blindness. The aim is to enhance the visual experience by adjusting image colors to be more distinguishable for those with various forms of CVD.

---
---

## Features

- **Image Recolorization:** Algorithms and methods to transform image colors to improve visibility for CVD individuals.
- **Color Vision Deficiency Simulation:** Tools to simulate different types of color blindness for testing and validation.
- **Web Interface:** An `index.html` and associated TypeScript/JavaScript files provide a web-based application for users to upload and recolor images.
- **Backend Processing:** Python scripts (`testing.py`, `xanax.py`) handle the core image processing and recolorization logic.
- **Configuration Management:** `.env` file for environment variable handling and configuration.

---



## Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/swar16/CVD-Image-Recolorization.git
    cd CVD-Image-Recolorization
    ```

2. **Install Frontend Dependencies:**
    ```bash
    npm install
    # or
    yarn install
    ```

3. **Install Python Dependencies:**
    *(You might want to use a virtual environment)*
    ```bash
    python -m venv venv
    # On Windows:
    venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate

    # If requirements.txt exists:
    pip install -r requirements.txt

    # Or install manually, e.g.:
    pip install opencv-python numpy
    ```

---

## Usage

### Running the Web Application

1. **Start the development server:**
    ```bash
    npm run dev
    # or
    yarn dev
    ```
    This will typically open the web application in your browser at a local address (e.g., `http://localhost:3000`).

2. **Upload and Recolor Images:**  
   Use the web interface to upload an image. The application will process and display the recolored version.

### Running Python Scripts

You can run the Python scripts directly for image processing tasks:

```bash
python testing.py
# or
python xanax.py
```

Refer to the comments or documentation within these Python files for specific usage and arguments.

---

