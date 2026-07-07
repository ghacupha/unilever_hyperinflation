To create a bank’s financial model generator that operates entirely in Python while adhering to the Financial Modeling Institute (FMI) standards, you can implement a pipeline that utilizes **Claude** for intelligence and research, and the **Modeleon** library to compile Python code into a fully linked, audit-ready Excel workbook.

The process follows these six phases to ensure the model is professional, transferable, and requires no manual Excel manipulation.

### 1. Research and Structural Design (Claude)
Before coding, use **Claude** as a research assistant to identify the specific drivers of the bank you are modeling. 
*   **Intelligence Gathering:** Prompt Claude to identify specific bank products, interest income streams, and macroeconomic drivers (e.g., interest rate curves, loan growth rates).
*   **Planning:** Claude can help you map out the required **10 Essential Schedules** required by FMI, including Revenue (Interest Income), Operating Costs, Tax, Working Capital, and detailed Debt/Equity schedules.
*   **Standard Alignment:** Use Claude to ensure your logic follows the FMI vertical format, which consolidates primary financial statements and schedules on a single master tab for easier electronic review and printing.

### 2. Environment Setup with Modeleon
Set up your Python environment (requires 3.12+) and import the `modeleon` library. This library acts as a Domain-Specific Language (DSL) that emits **live Excel formulas** rather than static values, allowing the final workbook to "breathe" when assumptions change.

### 3. Defining the Model "Engine" in Python
Instead of typing in Excel cells, you define Python objects that Modeleon translates into spreadsheet logic:
*   **Variables:** Use `mo.Variable()` for single inputs or formulas. Modeleon tracks dependencies automatically, ensuring full linkage across the model.
*   **Projections:** Use `mo.recurrence()` to create time-series projections (e.g., loan book growth). For example, `loans = mo.recurrence(start, "{prev} * (1 + {g})", g=growth_rate)`.
*   **Organization:** Group related data into `mo.MultiVariable()` containers. This keeps your Python code modular and matches the FMI practice of keeping all assumptions up front in a dedicated section.

### 4. Enforcing FMI Standards via Code
Modeleon allows you to programmatically enforce FMI rules so the resulting Excel file is "best-in-class" without manual formatting:
*   **No Hardcoding:** All values are defined as Python objects; Modeleon ensures formulas in Excel use references (e.g., `=B1*B2`) rather than embedded numbers.
*   **Single Entry Rule:** Variables are defined once in Python, and all subsequent uses reference that same object, preventing the error-prone practice of entering the same input twice.
*   **Vertical Consistency:** You can code the output to generate clean columnar data without blank columns between years, maintaining the horizontal continuity required for FMI vertical models.

### 5. Implementing Bank-Specific Mathematical Logic
Banks require unique capital structure modeling that can be complex to build manually:
*   **Cash Flow Sweep:** Code a sweep mechanism where excess cash automatically pays down revolving debt or draws from a revolver to fund shortfalls.
*   **Circularity Breakers:** Use Python logic to implement **Circularity Breakers**. Banks often have circular interest calculations (Interest $\rightarrow$ Net Income $\rightarrow$ Cash $\rightarrow$ Interest). In Python, you can wrap these in a logical switch: `=IF(Circ_Break="ON", 0, Average_Interest_Calculation)` to ensure the model remains stable and easy to debug.

### 6. Compilation, Audit, and Export
Once the Python script is complete, compile it to an `.xlsx` file. 
*   **Audit-Ready Linkage:** Every cell in the generated file will contain a live formula. A user can click any cell to verify precedents and trace linkages back to the original assumptions.
*   **Master Check Section:** Programmatically include a "Master Check" section at the front of the model. This compiles diagnostic tests, such as the **Balance Sheet Check** (Total Assets - Total Liabilities & Equity), displaying an "OK" or "ERROR" status automatically.
*   **Print Optimization:** Use Modeleon to set Excel's print-ready properties (Landscape orientation, 85-95% scaling, custom headers/footers with file paths and date stamps). 

The resulting file is a professional presentation that you can open and immediately **print to PDF** for senior decision-makers, fulfilling your goal of never having to touch the Excel file itself.