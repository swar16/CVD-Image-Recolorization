# CVD Image Recolorization

This repository contains a project focused on **recoloring images for individuals with Color Vision Deficiency (CVD)**, commonly known as color blindness. The aim is to enhance the visual experience by adjusting image colors to be more distinguishable for those with various forms of CVD.

---

## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [License](#license)

---

## Features

Based on the repository's files, this project likely offers the following features:

* **Image Recolorization:** Algorithms and methods to transform image colors to improve visibility for CVD individuals.
* **Color Vision Deficiency Simulation:** Potentially includes tools to simulate different types of color blindness for testing and validation.
* **Web Interface:** An `index.html` and associated TypeScript/JavaScript files suggest a web-based application for users to upload and recolor images.
* **Backend Processing:** Python scripts (`testing.py`, `xanax.py`) might handle the core image processing and recolorization logic.
* **Configuration Management:** `.env` file indicates environment variable handling for sensitive information or configuration.

---

## Technologies Used

This project utilizes a combination of frontend and backend technologies:

* **Frontend:**
    * **TypeScript:** For robust and scalable client-side logic.
    * **JavaScript:** Core web scripting language.
    * **HTML:** For the web application structure.
    * **Vite:** A fast build tool for modern web projects (`vite.config.ts`).
    * **ESLint:** For code quality and linting (`eslint.config.js`).
* **Backend/Processing:**
    * **Python:** For image processing and potentially the core recolorization algorithms (`testing.py`, `xanax.py`).
* **Package Management:**
    * `npm` or `yarn` (indicated by `package.json` and `package-lock.json`).

---

## Installation

To set up and run this project locally, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/swar16/CVD-Image-Recolorization.git](https://github.com/swar16/CVD-Image-Recolorization.git)
    cd CVD-Image-Recolorization
    ```

2.  **Install Frontend Dependencies:**
    ```bash
    npm install # or yarn install
    ```

3.  **Install Python Dependencies:**
    *(You might need to create a virtual environment first)*
    ```bash
    python -m venv venv
    source venv/bin/activate # On Windows: `venv\Scripts\activate`
    pip install -r requirements.txt # Assuming a requirements.txt will be added, or install manually:
    # pip install opencv-python numpy # (Common libraries for image processing in Python)
    ```

---

## Usage

### Running the Web Application

1.  **Start the development server:**
    ```bash
    npm run dev # or yarn dev
    ```
    This will typically open the web application in your browser at a local address (e.g., `http://localhost:3000`).

2.  **Upload and Recolor Images:** Use the web interface to upload an image. The application should then process and display the recolored version.

### Running Python Scripts (if applicable)

Individual Python scripts like `testing.py` or `xanax.py` might be runnable directly for specific processing tasks or testing:

```bash
python testing.py
# or
python xanax.py
